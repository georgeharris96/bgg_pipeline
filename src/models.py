# src/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Game(Base):
    __tablename__ = "Games"

    id = Column(Integer, primary_key=True)
    rank = Column(Integer)
    name = Column(String)

    def __repr__(self):
        return f"<Game(id={self.id}, name='{self.name}')"

def Statistics(Base):
    __tablename__ = "Statistics"

    id = Column(Integer, ForeignKey("Game.id"))
    description = Column(String)
    year_published = Column(Integer)
    min_players = Column(Integer)
    max_players = Column(Integer)
    suggested_num_player = Column(Integer)
    min_age = Column(Integer)
    average_rating = Column(Float)
    average_weight = Column(Float)

    def __repr__(self):
        return f"<Statistics(id={self.id}, description='{self.description}', year_published={self.year_published}, min_players={self.min_players}, max_players={self.max_players}, suggested_num_player={self.suggested_num_player}, min_age={self.min_age}, average_rating={self.average_rating}, average_weight={self.average_weight})>"

