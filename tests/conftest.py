import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, DATABASE_URL
import app.models


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(DATABASE_URL)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def session(engine):
    Session = sessionmaker(bind=engine, autoflush=False,
                           expire_on_commit=False)
    s = Session()
    yield s
    s.close()


@pytest.fixture
def clean_db(engine):
    """Очищает таблицы перед каждым тестом."""
    with engine.begin() as conn:
        conn.execute(Base.metadata.tables["orders"].delete())
        conn.execute(Base.metadata.tables["users"].delete())
    yield
