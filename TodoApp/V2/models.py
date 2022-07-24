from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # can have multiple indexes
    username = Column(String, unique=True, index=True)  # but why?
    first_name = Column(String)  # if nullable is not set to False, then can be NULL
    last_name = Column(
        String
    )  # which means that you mistype the attribute on the instance
    hashed_password = Column(
        String
    )  # then that attribute is not saved to db on .commit()
    is_active = Column(Boolean, default=True)

    todos = relationship(
        "Todos", back_populates="owner"
    )  # seems like documentation rather than column in table


class Todos(Base):
    __tablename__ = "todos"  # table name
    # specifying the column names and types
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(
        Integer, ForeignKey("users.id")
    )  # does Users table need a foreign key? Appears not

    owner = relationship(
        "Users", back_populates="todos"
    )  # seems like documentation rather than column in table
