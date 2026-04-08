from typing import Dict

from fastapi import FastAPI

from env import StartupOperationsEnv
from models import Action

app = FastAPI(title="Startup Operations OpenEnv", version="1.0.0")
runtime_env = StartupOperationsEnv()


@app.get("/")
def root() -> Dict[str, str]:
    return {"name": "startup-operations-openenv", "status": "ok"}


@app.post("/reset")
def reset() -> Dict[str, object]:
    obs = runtime_env.reset()
    return {"observation": obs.model_dump(), "done": False}


@app.post("/step")
def step(action: Action) -> Dict[str, object]:
    obs, reward, done, info = runtime_env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward.value,
        "done": done,
        "info": info,
    }


@app.get("/state")
def state() -> Dict[str, object]:
    return runtime_env.state()
