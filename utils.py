"""Deterministic charging-station benchmark and shared data utilities.

Source: Mathematical Optimization (VU Amsterdam) starter materials;
external data and plotting helpers: github.com/alessandrozocca/MO2025.
"""

import pyomo.environ as pyo
import httpimport

with httpimport.github_repo("alessandrozocca", "MO2025"):
    from helpers.assignment2 import (
        make_static_data,
        make_demand_scenarios,
        plot_instance,
        plot_solution,
    )


# Deterministic charging-station model.
def create_model(
    stations: list[int],
    neighborhoods: list[int],
    fixed_costs: list[int],
    travel_costs: dict[tuple[int, int], int],
    penalty_unmet_demand: int,
    max_chargers: list[int],
    demands: list[int],
):
    """
    Model for the charging station placement problem.

    Parameters
    ----------
    stations
        List of indices where charging stations can be placed.
    neighborhoods
        List of indices of neighborhoods.
    fixed_costs
        Fixed cost of opening a charging station at a location.
    travel_costs
        Travel costs between locations. Entry (i, j) gives the cost
        of traveling from station i to neighborhood j.
    penalty_unmet_demand
        Penalty term for each unit of unmet demand.
    demands
        List of demands for each neighborhood.
    """
    model = pyo.ConcreteModel()

    model.M = pyo.Set(initialize=stations)
    model.V = pyo.Set(initialize=neighborhoods)

    model.f = fixed_costs
    model.c = travel_costs
    model.p = penalty_unmet_demand
    model.d = demands

    model.x = pyo.Var(model.M, domain=pyo.NonNegativeIntegers)
    model.y = pyo.Var(model.M, model.V, domain=pyo.NonNegativeIntegers)
    model.u = pyo.Var(model.V, domain=pyo.NonNegativeReals)

    @model.Expression()
    def total_fixed_cost(m):
        return sum(m.f[i] * m.x[i] for i in m.M)

    @model.Expression()
    def total_travel_cost(m):
        return sum(m.c[i, j] * m.y[i, j] for i in m.M for j in m.V)

    @model.Expression()
    def total_penalty_cost(m):
        return sum(m.p * m.u[j] for j in m.V)

    @model.Objective(sense=pyo.minimize)
    def objective(m):
        return m.total_fixed_cost + m.total_travel_cost + m.total_penalty_cost

    @model.Constraint(model.V)
    def demand_equation(m, j):
        return sum(m.y[i, j] for i in m.M) + m.u[j] == m.d[j]

    @model.Constraint(model.M)
    def charging_station_capacity(m, i):
        return sum(m.y[i, j] for j in m.V) <= m.x[i]

    @model.Constraint(model.M)
    def max_chargers_per_station(m, i):
        return m.x[i] <= max_chargers[i]

    return model
