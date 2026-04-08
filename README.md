---
title: startup-operations-openenv
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Startup Operations OpenEnv

A complete, real-world OpenEnv environment that simulates startup operations: budget allocation, hiring, product development, growth, and support quality under realistic constraints.

## Why This Is Real-World

Early-stage teams make daily trade-offs between growth and survival. This environment models those choices with costs, churn, revenue, incidents, and customer satisfaction pressure.

## OpenEnv Compliance

- Typed models: `Observation`, `Action`, `Reward` in `models/`
- API methods: `reset()`, `step(action)`, `state()` in `env/environment.py`
- Metadata: `openenv.yaml`
- 3 deterministic graders: `tasks/easy.py`, `tasks/medium.py`, `tasks/hard.py`

## Project Structure

```text
project-name/
|
|-- env/
|   |-- __init__.py
|   |-- environment.py
|   |-- dynamics.py
|   |-- validation.py
|   |-- utils.py
|
|-- models/
|   |-- __init__.py
|   |-- state.py
|   |-- action.py
|   |-- reward.py
|
|-- tasks/
|   |-- __init__.py
|   |-- easy.py
|   |-- medium.py
|   |-- hard.py
|
|-- agents/
|   |-- __init__.py
|   |-- baseline_agent.py
|
|-- data/
|   |-- logs.jsonl
|   |-- memory.json
|
|-- inference.py
|-- main.py
|-- openenv.yaml
|-- Dockerfile
|-- requirements.txt
|-- README.md
```

## Action Space

- `hire`: increase team size and future throughput, but raises burn.
- `market`: acquire users quickly, but costs cash and may affect quality.
- `build`: improve product quality to reduce churn and improve revenue.
- `support`: improve customer satisfaction and retention.
- `idle`: minimal spend; penalized if repeated excessively.

## Observation Space

- `day`
- `money`
- `users`
- `team_size`
- `product_quality`
- `customer_satisfaction`
- `market_demand`
- `burn_rate`
- `last_action`

## Reward Design

Step reward is continuous and clamped to `[0.0, 1.0]`.

Positive signals:
- user acquisition momentum
- product quality
- financial runway
- customer satisfaction

Negative signals:
- low cash runway
- repeated idle loops
- risky hiring when funds are too low

## Tasks and Deterministic Graders

All task scores are deterministic and clamped to `[0.0, 1.0]`.

1. Easy (`tasks.easy:grade_easy`)
Objective: stay solvent and avoid bankruptcy.
Target score band: `0.8 - 1.0`

2. Medium (`tasks.medium:grade_medium`)
Objective: grow users while improving quality.
Target score band: `0.5 - 0.8`

3. Hard (`tasks.hard:grade_hard`)
Objective: optimize efficiency, cash health, and satisfaction.
Target score band: `0.1 - 0.5`

## Setup

```bash
pip install -r requirements.txt
```

Set required variables:

```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="<your_api_key>"
export OPENAI_API_KEY="<optional_fallback_key>"
```

On Windows PowerShell:

```powershell
$env:API_BASE_URL="https://api.openai.com/v1"
$env:MODEL_NAME="gpt-4o-mini"
$env:HF_TOKEN="<your_api_key>"
$env:OPENAI_API_KEY="<optional_fallback_key>"
```

## Run Baseline Inference

```bash
python inference.py
```

The script emits structured logs in strict format:
- `[START] task=... env=... model=...`
- `[STEP] step=... action=... reward=... done=... error=...`
- `[END] success=... steps=... score=... rewards=[...]`

## Baseline Reproducibility

- Fixed random seed (`SEED`, default `42`)
- Deterministic graders
- `temperature=0.0` for model calls
- Heuristic fallback if API call fails to ensure script completion

## Run API Server (for local validation / HF Space)

```bash
uvicorn main:app --host 0.0.0.0 --port 7860
```

Endpoints:
- `POST /reset`
- `POST /step`
- `GET /state`

## Docker

```bash
docker build -t startup-openenv .
docker run --rm -p 7860:7860 startup-openenv
```

Then test:

```bash
curl -X POST http://localhost:7860/reset
```

## OpenEnv Validation

```bash
openenv validate
```

If your installed validator expects specific schema keys, adjust `openenv.yaml` key names while keeping the same environment API and model references.