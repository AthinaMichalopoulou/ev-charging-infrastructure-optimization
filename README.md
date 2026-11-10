# EV Charging Infrastructure Optimization under Uncertain Demand

**Deterministic benchmarking · Two-stage stochastic optimization · Chance-constrained capacity planning**

## Project overview

Planning electric-vehicle charging infrastructure involves two linked decisions: **where to install chargers** and **how much capacity to provide**. These decisions must account for uncertain future demand while balancing installation expense, travel costs, and the penalty for charging demand that cannot be served.

This project formulates EV charging infrastructure planning as a series of mixed-integer optimization problems, implemented in **Python with Pyomo**. It uses a Manhattan-based planning instance and **365 daily demand scenarios** to explore how uncertainty and risk tolerance affect investment decisions.

## The planning problem

Each candidate station location has a construction cost and a maximum number of chargers. Neighborhoods generate charging demand, which can be assigned to stations at a travel-related cost. Any demand that cannot be met incurs a penalty.

The key difficulty is **timing**: capacity must be installed before the actual demand of a particular day becomes known. Designing for each individual scenario separately may produce optimistic results, because real infrastructure cannot be rebuilt daily. A practical plan therefore needs to perform across many potential demand realizations.

The project explores this problem through three related models.

## Optimization models

### 1. Deterministic benchmark

The deterministic model optimizes charging capacity and demand allocation separately for each of the 365 demand scenarios. It minimizes installation, assignment, and unmet-demand costs subject to capacity and demand-balance constraints.

Its scenario-average objective provides a **perfect-information benchmark**: a reference for how cheaply demand could be served if infrastructure could be tailored to each day's demand.

### 2. Two-stage stochastic optimization

The stochastic model separates decisions into two stages:

- **First stage:** choose station capacities before the daily demand is known.
- **Second stage:** allocate realized demand to stations and account for unmet demand in each scenario.

A single first-stage capacity plan is optimized against the expected operational costs across all scenarios. This makes the uncertainty in daily demand part of the infrastructure decision itself.

### 3. Chance-constrained capacity planning

The chance-constrained model takes a different view of capacity planning. Instead of explicitly modeling neighborhood-level allocations, it considers **total installed capacity relative to aggregate demand** and a tolerated deviation.

Two parameters control the planning requirement: **ε**, the permitted proportion of demand scenarios that may violate a mismatch constraint, and **Δ**, the allowable mismatch between installed capacity and demand. The notebook studies how varying these parameters affects feasibility, capacity, and construction cost.

## Results and observations

| Model | Saved objective value |
| --- | ---: |
| Deterministic benchmark (mean over scenarios) | 16,857.06 |
| Two-stage stochastic optimization | 17,107.43 |
| Chance-constrained model (ε = 0.2, Δ = 150) | 4,529.00 |

The stochastic objective exceeds the deterministic benchmark because it must select one infrastructure plan without knowing the future scenario. The chance-constrained objective measures **installation cost under a different model**, so it should not be compared directly with the two preceding total-cost figures.

The saved sensitivity analysis illustrates how greater risk tolerance or larger allowable demand mismatch can reduce required capacity and cost, while stricter requirements may be infeasible.

## Project files

- [Mathematical formulation](docs/model_formulation.md): sets, parameters, objectives and constraints for all three models, matched to the Pyomo implementation.
- [Results and interpretation](results/README.md): objective values, scenario comparison and chance-constraint sensitivity analysis.
- [Optimization notebook](notebooks/ev_charging_optimization.ipynb): Pyomo implementations, figures and results.
- [`utils.py`](utils.py): deterministic baseline and data/plotting utilities.

## Tools and reproducibility

The models use **Pyomo** with the **HiGHS** solver. The scenario and visualization workflows use **NumPy** and **Matplotlib**. Data generation and plotting helpers are imported through `utils.py` from the [MO2025 helper repository](https://github.com/alessandrozocca/MO2025) using `httpimport`.

Install the listed packages with `pip install -r requirements.txt` and ensure the external helper repository is accessible before running the notebook. The notebook includes numerical results and figures that can be inspected directly on GitHub. See the [results document](results/README.md) for interpretation and caveats.

## Acknowledgement

This project originated from Mathematical Optimization coursework at **Vrije Universiteit Amsterdam (2025–2026)**. The problem setting and selected utility code were provided in the course materials.
