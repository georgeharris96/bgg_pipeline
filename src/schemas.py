# src/schemas.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class GameRankCreate(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore", # ignore extra fields
        )
    
    id: int
    rank: int
    name: str


    @field_validator("rank")
    def validate_rank(cls, value):
        if value <= 0:
            raise ValueError("Rank must be a positive integer")
        return value
    
    @field_validator("id")
    def validate_id(cls, value):
        if value <= 0:
            raise ValueError("id must be a postive integer")
        return value


class GameStatistics(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        )
    
    id: int
    description: str
    year_published: int
    min_players: int
    max_players: int
    suggested_num_player: int
    min_age: int
    average_rating: float
    average_weight: float

    @field_validator("id")
    def validate_id(cls, value):
        if value <= 0:
            raise ValueError("id must be a postive integer")
        return value
    

    @field_validator("year_published")
    def validate_year_published(cls, value):
        if value > datetime.now().year:
            raise ValueError(f"year_published must be greater than {datetime.now().year}")
        return value
    

    @field_validator("min_players")
    def validate_min_players(cls, value):
        if value <= 0:
            raise ValueError("min_players must be a postive integer")
        return value
    

    @field_validator("max_players")
    def validate_max_players(cls, value):
        if value <= 0:
            raise ValueError("max_players must be a positive integer")
        return value
    

    @field_validator("suggested_num_players")
    def validate_suggested_num_players(cls, value):
        if value <= 0:
            raise ValueError("suggestd_num_players must be a positive integer")
        return value


    @field_validator("min_age")
    def validate_min_age(cls, value):
        if value <= 0:
            raise ValueError("min_age must be a postive integer")
        return value
    

    @field_validator("average_rating")
    def validate_average_rating(cls, value):
        if value < 0:
            raise ValueError("average_rating cannot be negative")
        return value


    @field_validator("average_weight")
    def validate_average_weight(cls, value):
        if value < 0:
            raise ValueError("average_weight cannot be negative")
        return value
    

    @model_validator(mode="after")
    def validate_players(self):
        if self.max_players < self.min_players:
            raise ValueError("max_players must be greater than or equal to min_players")
        return self


class GameMechanic(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        )
    
    id: int
    mechanic_name: str

    @field_validator("id")
    def validate_id(cls, value):
        if value <= 0:
            raise ValueError("id must be a positive integer")
        return value