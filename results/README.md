# Results and interpretation

This section presents the optimization results, compares the deterministic and stochastic approaches, and examines how risk tolerance and allowable demand mismatch influence charging infrastructure decisions.

## Scenario comparison

| Optimization model | Objective value | Interpretation |
|---|---:|---|
| Deterministic benchmark, average of 365 independently optimized days | 16,857.06 | Total installation, assignment and unmet-demand cost, with perfect daily demand information |
| Two-stage stochastic model | 17,107.43 | Expected total cost, with a single installed capacity plan shared across scenarios |
| Implemented chance-constrained model ($\epsilon=0.2$, $\Delta=150$) | 4,529.00 | Installation cost only, under the implemented aggregate-demand constraints |

The stochastic objective is **250.38 higher** than the deterministic benchmark (about **1.49%**). This reflects the price of selecting installed capacity before demand is revealed, whereas the deterministic model can tailor infrastructure to each day. The chance-constrained model has a different objective and cannot be compared directly with the first two cost values.

## Risk tolerance: varying $\epsilon$

At fixed $\Delta=150$, the experiments show infeasibility at $\epsilon=0.0$ and $0.1$, with feasible solutions from $\epsilon=0.2$ through $1.0$. Within feasible runs, greater violation tolerance generally permits fewer installed chargers and a lower installation cost. At $\epsilon=1$, the analysis finds a zero-installation solution.

## Allowed mismatch: varying $\Delta$

At fixed $\epsilon=0.2$, the experiments show infeasibility for tested $\Delta=70,80,\ldots,130$ and feasibility for tested $\Delta=140,150,\ldots,300$. Relaxing the permitted mismatch makes the installation decision less restrictive and can lower installed capacity and cost.

The notebook contains the saved histogram, instance views, spatial visualization and sensitivity plots. See [notebooks/ev_charging_optimization.ipynb](../notebooks/ev_charging_optimization.ipynb).

## Interpretation caveats

- The chance-constrained Pyomo code uses **separate upper and lower violation budgets**, not a single joint chance constraint. The mathematical document describes this exactly.
- The stochastic solution plotting cell references `build_decisions`, although the optimized decision is stored in `build_decision`. Consequently, the saved spatial plot should not be treated as verified visualization of the stochastic solution.
