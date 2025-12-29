# src/schemas.py
from pydantic import BaseModel, HttpUrl, ConfigDict


class GameRankCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: int
    rank: int
    name: str