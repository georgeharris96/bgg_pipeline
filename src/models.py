# src/models.py
from sqlalchemy import Column, Integer, String
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
    