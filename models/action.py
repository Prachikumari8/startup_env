from typing import Literal

from pydantic import BaseModel


class Action(BaseModel):
    action_type: Literal["hire", "market", "build", "support", "idle"]
