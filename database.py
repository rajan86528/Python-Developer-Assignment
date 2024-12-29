
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/formdb")

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    async with SessionLocal() as session:
        yield session

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Form(Base):
    __tablename__ = "forms"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    submissions = relationship("Submission", back_populates="form", cascade="all, delete-orphan")


class Field(Base):
    __tablename__ = "fields"
    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"))
    field_id = Column(String, nullable=False)
    type = Column(String, nullable=False)
    label = Column(String, nullable=False)
    required = Column(Boolean, nullable=False)

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"))
    field_id = Column(String, nullable=False)
    value = Column(JSON)
    form = relationship("Form", back_populates="submissions")
