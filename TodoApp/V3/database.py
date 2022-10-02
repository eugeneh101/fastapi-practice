from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"
# SQLALCHEMY_DATABASE_URL = (
#     "postgresql://postgres:password@localhost/TodoApplicationDatabase"
# )

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # used by sqlite
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)  # instance of a db session
Base = declarative_base()  # database model
# probably instantiated here to be used across multiple model files
