# Mathematical formulation

The planning instance places electric-vehicle charging capacity at candidate locations in Manhattan and allocates neighborhood demand to that capacity. The mathematical models below describe the **existing implementations**, not new variants. The deterministic and stochastic objectives include installation, travel and unmet-demand costs; the chance-constrained objective includes installation cost only.

## Sets, parameters and variables

| Symbol | Meaning |
|---|---|
| $M$ | Candidate charging locations, indexed by $i$ |
| $V$ | Neighborhoods generating demand, indexed by $j$ |
| $\Omega$ | 365 equally likely daily demand scenarios, indexed by $\omega$ |
| $f_i$ | Construction cost per charger at candidate location $i$ |
| $c_{ij}$ | Travel-related cost for serving demand from neighborhood $j$ at station $i$ |
| $p_j$ | Penalty per unit of unmet demand in neighborhood $j$; the code uses a shared penalty $p$ |
| $K_i$ | Maximum installable charging capacity at location $i$ |
| $d_j(\omega)$ | Neighborhood $j$ demand in scenario $\omega$ |
| $x_i$ | Installed chargers at location $i$; nonnegative integer |
| $y_{ij}(\omega)$ | Demand of $j$ served by station $i$ in scenario $\omega$; nonnegative integer |
| $u_j(\omega)$ | Unmet neighborhood demand in scenario $\omega$; nonnegative (integer in stochastic implementation) |

The deterministic model uses a fixed daily demand vector $d_j$ and omits the scenario index from allocation and unmet-demand variables.

## Deterministic model

For a known daily demand vector, minimize the total installation, travel and unmet-demand cost:

$$
\min_{x,y,u}\quad \sum_{i\in M}f_i x_i+\sum_{i\in M}\sum_{j\in V}c_{ij}y_{ij}+\sum_{j\in V}p_j u_j.
$$

Subject to demand balance, available charging capacity and maximum installation capacity:

$$
\sum_{i\in M}y_{ij}+u_j=d_j\quad(\forall j\in V),
$$
$$
\sum_{j\in V}y_{ij}\leq x_i\quad(\forall i\in M),\qquad 0\leq x_i\leq K_i\quad(\forall i\in M).
$$

In the implementation, $x_i$ and $y_{ij}$ are nonnegative integers and $u_j$ is nonnegative continuous. The course baseline `create_model()` appears in [`utils.py`](../utils.py). Solving this model separately for each of 365 scenarios and averaging the optimal values produces the perfect-information benchmark $C_{det}$.

## Two-stage stochastic model

The first-stage capacity decision $x_i$ is chosen **before** the day’s demand is observed. Assignment $y_{ij}(\omega)$ and unmet demand $u_j(\omega)$ are chosen **after** scenario $\omega$ is realized.

The recourse problem for fixed installed capacity $x$ and scenario $\omega$ is

$$
Q(x,\omega)=\min_{y(\omega),u(\omega)}\left[\sum_{i\in M}\sum_{j\in V}c_{ij}y_{ij}(\omega)+\sum_{j\in V}p_j u_j(\omega)\right],
$$

subject to

$$
\sum_{i\in M}y_{ij}(\omega)+u_j(\omega)=d_j(\omega)\quad(\forall j\in V),
$$
$$
\sum_{j\in V}y_{ij}(\omega)\leq x_i\quad(\forall i\in M),
$$

and nonnegative allocation and unmet-demand variables. The first-stage model minimizes

$$
\min_{x}\quad \sum_{i\in M}f_i x_i+\mathbb E_{\omega}[Q(x,\omega)],
\qquad x_i\in\mathbb Z_{\geq 0},\quad x_i\leq K_i.
$$

### Extensive-form MILP

The finite, equally likely scenarios give a single optimization problem:

$$
\min_{x,y,u}\quad \sum_{i\in M}f_i x_i +\frac{1}{365}\sum_{\omega\in\Omega}\left[\sum_{i\in M}\sum_{j\in V}c_{ij}y_{ij}(\omega)+\sum_{j\in V}p_j u_j(\omega)\right]
$$

subject to, for every $\omega\in\Omega$,

$$
\sum_{i\in M}y_{ij}(\omega)+u_j(\omega)=d_j(\omega)\quad(\forall j\in V),
$$
$$
\sum_{j\in V}y_{ij}(\omega)\le x_i\quad(\forall i\in M),\qquad x_i\le K_i\quad(\forall i\in M).
$$

The Pyomo model declares $x_i$, $y_{ij}(\omega)$ and $u_j(\omega)$ as nonnegative integers. **One** capacity decision $x_i$ is shared by all 365 scenarios, unlike the deterministic benchmark. See `create_stochastic_model` in the [notebook](../notebooks/ev_charging_optimization.ipynb).

## Chance-constrained capacity model

This is a **different simplified planning model** that considers aggregate demand and installation cost; it does not use the neighborhood-to-station allocation decisions from the first two models.

Let total demand in scenario $\omega$ be

$$D(\omega)=\sum_{j\in V}d_j(\omega),$$

and total installed capacity be $X=\sum_{i\in M}x_i$. The planning aim is to keep the absolute mismatch $|D(\omega)-X|$ at most $\Delta$ in a sufficiently large proportion of demand scenarios, with risk tolerance $\epsilon$.

### Implemented mixed-integer formulation

The code uses **two** binary indicators per scenario, $z_\omega^+$ and $z_\omega^-$, and a shared large constant $M_{big}$:

$$
\min_x\quad \sum_{i\in M} f_i x_i
$$

subject to

$$
D(\omega)-X\le \Delta+M_{big}z_\omega^+\quad(\forall\omega\in\Omega),
$$
$$
X-D(\omega)\le \Delta+M_{big}z_\omega^-\quad(\forall\omega\in\Omega),
$$
$$
\sum_{\omega\in\Omega}z_\omega^+\le \epsilon|\Omega|,\qquad
\sum_{\omega\in\Omega}z_\omega^-\le \epsilon|\Omega|,
$$
$$
0\le x_i\le K_i,\quad x_i\in\mathbb Z;\qquad
z_\omega^+,z_\omega^-\in\{0,1\}.
$$

The notebook sets `M_big = max(aggregate_demands) + sum(static_data.max_chargers)` and evaluates $\epsilon=0.2$, $\Delta=150$ before running sensitivity experiments.

**Interpretation / limitation:** These two separate violation budgets enforce the *upper* and *lower* mismatch requirements individually. They are **not generally equivalent** to a single joint chance constraint $\mathbb P(|D(\omega)-X|\le\Delta)\ge 1-\epsilon$: the sets of scenarios violating the two inequalities can differ. A joint formulation could instead use one scenario indicator for both inequalities and one violation budget. The implementation and reported results concern the separate-budget formulation, not the stronger joint chance constraint.

## Sensitivity analysis

The notebook repeats the implemented chance-constrained optimization while varying $\epsilon$ at $\Delta=150$ and while varying $\Delta$ at $\epsilon=0.2$. It compares feasibility, total installed capacity and installation cost. See the [results](../results/README.md) and saved figures in the [notebook](../notebooks/ev_charging_optimization.ipynb).
