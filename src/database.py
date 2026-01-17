#src/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Create the SQLite engine
DATABASE_URL = "sqlite:///./data/bgg_data.db"
engine = create_engine(DATABASE_URL)

# Create a configured Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables defined in your models.
Base.metadata.create_all(bind=engine)