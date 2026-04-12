import json
import os
import argparse
import random
from typing import Dict, List, Tuple

from openai import OpenAI

from agents.baseline_agent import heuristic_action
from env import StartupOperationsEnv
from models import Action
from tasks import grade_easy, grade_hard, grade_medium

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.getenv("HF_TOKEN")
MAX_STEPS = int(os.getenv("MAX_STEPS", "30"))
SEED = int(os.getenv("SEED", "42"))
VERBOSE_STEPS = os.getenv("VERBOSE_STEPS", "0") == "1"
STEP_SAMPLE_EVERY = max(1, int(os.getenv("STEP_SAMPLE_EVERY", "5")))
BENCHMARK = "startup-operations-openenv"
SCORE_BANDS = {
    "easy": (0.8, 1.0),
    "medium": (0.5, 0.8),
    "hard": (0.1, 0.5),
}


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: str | None) -> None:
    base = f"[STEP] step={step} action={action} reward={reward:.6f} done={str(done).lower()}"
    if error:
        base = f"{base} error={error}"
    print(base, flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = json.dumps([round(v, 6) for v in rewards])
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.6f} rewards={rewards_str}",
        flush=True,
    )


def print_steps_summary(step_list: List[Tuple[int, str, float]], compact: bool = True) -> None:
    print("\n=== STEP-BY-STEP BREAKDOWN ===", flush=True)
    print(f"{'Step':>4} | {'Action':>8} | {'Reward':>8} | Progress", flush=True)
    print("-" * 50, flush=True)

    max_reward = max([r for _, _, r in step_list]) if step_list else 1.0

    if compact:
        # Keep output concise: first, sampled, and final steps.
        selected = []
        for index, item in enumerate(step_list):
            step, _, _ = item
            if index == 0 or index == len(step_list) - 1 or step % STEP_SAMPLE_EVERY == 0:
                selected.append(item)
    else:
        selected = step_list

    for step, action, reward in selected:
        bar_length = 15
        filled = int((reward / max_reward) * bar_length)
        bar = "=" * filled + "-" * (bar_length - filled)
        print(f"{step:4d} | {action:>8} | {reward:8.3f} | {bar}", flush=True)


def classify_outcome(level: str, score: float) -> str:
    low, high = SCORE_BANDS[level]
    midpoint = (low + high) / 2.0
    if score < low or score > high:
        return "FAIL"
    return "PASS" if score >= midpoint else "IMPROVE"


def print_human_summary(level: str, score: float, final_state: Dict[str, float], seed: int) -> None:
    status = classify_outcome(level, score)

    print("\n=== RUN SUMMARY ===", flush=True)
    print(f"Level  : {level}", flush=True)
    print(f"Seed   : {seed}", flush=True)
    print(f"Score  : {score:.3f} ({status})", flush=True)
    print("\nFinal state:", flush=True)
    print(
        f"money={final_state['money']}, users={final_state['users']}, "
        f"team={final_state['team_size']}, product={final_state['product_quality']}, "
        f"satisfaction={final_state['customer_satisfaction']}, status={final_state['status']}",
        flush=True,
    )


def get_model_action(client: OpenAI, state: Dict[str, float], history: List[str]) -> str:
    prompt = (
        "You are operating a startup. Choose exactly one action from: "
        "hire, market, build, support, idle. Return only the action word.\n"
        f"State: {json.dumps(state, sort_keys=True)}\n"
        f"History: {history[-4:]}"
    )
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.0,
            top_p=1.0,
            messages=[{"role": "user", "content": prompt}],
        )
        text = (response.choices[0].message.content or "").strip().lower()
        action = text.split()[0] if text else "idle"
        if action not in {"hire", "market", "build", "support", "idle"}:
            return heuristic_action(state)
        return action
    except Exception as exc:
        if not getattr(get_model_action, "_error_logged", False):
            print(f"[DEBUG] Model request failed (showing once): {exc}", flush=True)
            setattr(get_model_action, "_error_logged", True)
        return heuristic_action(state)


def run_task(task_name: str, grader, seed: int, api_key: str | None) -> Tuple[float, List[float], Dict[str, float]]:
    env = StartupOperationsEnv(max_days=MAX_STEPS, seed=seed)
    if api_key:
        client = OpenAI(base_url=API_BASE_URL, api_key=api_key)
    else:
        client = OpenAI(base_url=API_BASE_URL, api_key="missing")

    history: List[str] = []
    rewards: List[float] = []
    steps_info: List[Tuple[int, str, float]] = []
    score = 0.0
    steps_taken = 0

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    result_obs = env.reset(seed=seed)
    done = False
    for step in range(1, MAX_STEPS + 1):
        if done:
            break

        state = env.state()
        if api_key:
            action_text = get_model_action(client, state, history)
        else:
            action_text = heuristic_action(state)

        try:
            action = Action(action_type=action_text)
            result_obs, reward, done, info = env.step(action)
            reward_value = float(reward.value)
            rewards.append(reward_value)
            steps_info.append((step, action_text, reward_value))
            history.append(f"{step}:{action_text}:{reward_value:.4f}")
            steps_taken = step
            if VERBOSE_STEPS or done or step == 1 or step % STEP_SAMPLE_EVERY == 0:
                log_step(step=step, action=action_text, reward=reward_value, done=done, error=None)
        except Exception as exc:
            log_step(step=step, action=action_text, reward=0.0, done=True, error=str(exc))
            done = True

    final_state = env.state()
    score = float(grader(final_state))
    success = classify_outcome(task_name, score) == "PASS"
    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    print_steps_summary(steps_info, compact=not VERBOSE_STEPS)
    return score, rewards, final_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run startup environment inference for all levels.")
    parser.add_argument(
        "--seed",
        required=False,
        type=int,
        help="Optional base seed. If omitted, random seeds are used.",
    )
    return parser.parse_args()


def resolve_seed(base_seed: int | None, offset: int) -> int:
    if base_seed is None:
        return random.SystemRandom().randint(1, 2_147_483_647)
    return base_seed + offset


def main() -> None:
    args = parse_args()
    api_key = API_KEY

    graders = {
        "easy": grade_easy,
        "medium": grade_medium,
        "hard": grade_hard,
    }

    levels = ["easy", "medium", "hard"]
    results = []
    for index, level in enumerate(levels):
        seed = resolve_seed(args.seed, index)
        score, _, final_state = run_task(level, graders[level], seed=seed, api_key=api_key)
        result = {
            "level": level,
            "seed": seed,
            "score": round(score, 6),
            "final_state": final_state,
        }
        results.append(result)
        print_human_summary(level=level, score=score, final_state=final_state, seed=seed)

    if os.getenv("OUTPUT_JSON", "0") == "1":
        print("\n=== RAW JSON ===", flush=True)
        print(json.dumps({"runs": results}, indent=2), flush=True)


if __name__ == "__main__":
    main()
