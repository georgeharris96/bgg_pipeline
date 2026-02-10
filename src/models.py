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

class Statistics(Base):
    __tablename__ = "Statistics"

    id = Column(Integer, ForeignKey("Games.id"), primary_key=True)
    description = Column(String)
    year_published = Column(Integer)
    min_players = Column(Integer)
    max_players = Column(Integer)
    suggested_num_player = Column(Integer)
    min_age = Column(Integer)
    average_rating = Column(Float)
    average_weight = Column(Float)

    def __repr__(self):
        return f"<Statistics object for boardgame of id {self.id}>"

class Mechanics(Base):
    __tablename__ = "Mechanics"

    id = Column(Integer, ForeignKey("Games.id"), primary_key=True)
    mechanic = Column(String)

    def __repr__(self):
        return f"<boardgame of id: {self.id} has the mechanic: {self.mechanic}>"