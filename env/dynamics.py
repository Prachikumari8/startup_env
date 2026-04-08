from __future__ import annotations

from random import Random
from typing import Dict


def apply_action(state: Dict[str, float], action: str, rng: Random) -> Dict[str, float]:
    money = float(state["money"])
    users = int(state["users"])
    team_size = int(state["team_size"])
    product_quality = float(state["product_quality"])
    customer_satisfaction = float(state["customer_satisfaction"])
    market_demand = float(state["market_demand"])

    expense = 0.0
    gross_new_users = 0

    if action == "hire":
        team_size += 1
        expense += 170.0
        customer_satisfaction += 0.02
    elif action == "market":
        expense += 90.0
        gross_new_users = int(rng.randint(8, 28) * market_demand * max(product_quality, 0.6))
        users += gross_new_users
        customer_satisfaction -= 0.01
    elif action == "build":
        expense += 110.0
        product_quality += 0.16
        customer_satisfaction += 0.03
    elif action == "support":
        expense += 70.0
        customer_satisfaction += 0.08
    elif action == "idle":
        expense += 10.0

    burn_rate = 35.0 + (team_size * 28.0)
    money -= (expense + burn_rate)

    churn_ratio = max(0.01, 0.06 - (0.015 * product_quality) - (0.03 * customer_satisfaction))
    churned_users = int(users * churn_ratio)
    users = max(0, users - churned_users)

    revenue = users * (1.05 + (0.3 * product_quality))
    money += revenue

    if rng.random() < 0.12:
        incident_cost = rng.randint(40, 120)
        money -= incident_cost

    market_demand = max(0.75, min(1.35, market_demand + rng.uniform(-0.04, 0.05)))
    customer_satisfaction = max(0.0, min(1.0, customer_satisfaction))

    return {
        "money": money,
        "users": users,
        "team_size": team_size,
        "product_quality": product_quality,
        "customer_satisfaction": customer_satisfaction,
        "market_demand": market_demand,
        "burn_rate": burn_rate,
        "gross_new_users": gross_new_users,
        "churned_users": churned_users,
        "revenue": revenue,
        "expense": expense,
    }
