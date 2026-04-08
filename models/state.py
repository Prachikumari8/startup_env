from pydantic import BaseModel, Field


class Observation(BaseModel):
    day: int = Field(ge=0)
    money: float = Field(ge=0.0)
    users: int = Field(ge=0)
    team_size: int = Field(ge=1)
    product_quality: float = Field(ge=0.0)
    customer_satisfaction: float = Field(ge=0.0, le=1.0)
    market_demand: float = Field(ge=0.0)
    burn_rate: float = Field(ge=0.0)
    last_action: str
