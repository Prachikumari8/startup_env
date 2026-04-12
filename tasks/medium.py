from __future__ import annotations

from typing import Dict

from tasks.common import clamp01, clamp_strict, require_valid_final_state


def grade_medium(state: Dict[str, float]) -> float:
    require_valid_final_state(state)

    users = float(state["users"])
    product_quality = float(state["product_quality"])
    money = float(state["money"])
    satisfaction = clamp01(float(state["customer_satisfaction"]))

    growth_score = clamp01(users / 1200.0)
    quality_score = clamp01((product_quality - 0.9) / 1.3)
    economics_score = clamp01(money / 5500.0)
    balance_penalty = abs(growth_score - quality_score)

    base = (0.45 * growth_score) + (0.30 * quality_score) + (0.15 * economics_score) + (0.10 * satisfaction)
    score = clamp_strict((0.60 * base) + 0.23 - (0.08 * balance_penalty))
    return round(score, 6)
