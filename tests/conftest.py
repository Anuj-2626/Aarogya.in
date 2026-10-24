import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from Backend.app.main import app
from Backend.app.database import Base, get_db as database_get_db

from Backend.app.routers.answers import get_db as answers_get_db
from Backend.app.routers.auth import get_db as auth_get_db
from Backend.app.routers.consents import get_db as consents_get_db
from Backend.app.routers.doctor_dashboard import get_db as doctor_dashboard_get_db
from Backend.app.routers.documents import get_db as documents_get_db
from Backend.app.routers.fhir import get_db as fhir_get_db
from Backend.app.routers.interviews import get_db as interviews_get_db
from Backend.app.routers.patients import get_db as patients_get_db
from Backend.app.routers.questions import get_db as questions_get_db
from Backend.app.routers.safety import get_db as safety_get_db
from Backend.app.routers.sessions import get_db as sessions_get_db
from Backend.app.routers.summaries import get_db as summaries_get_db
from Backend.app.routers.timeline import get_db as timeline_get_db

from Backend.app.security import get_db as security_get_db


TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()

    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())

    db.commit()

    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[database_get_db] = override_get_db

    app.dependency_overrides[answers_get_db] = override_get_db
    app.dependency_overrides[auth_get_db] = override_get_db
    app.dependency_overrides[consents_get_db] = override_get_db
    app.dependency_overrides[doctor_dashboard_get_db] = override_get_db
    app.dependency_overrides[documents_get_db] = override_get_db
    app.dependency_overrides[fhir_get_db] = override_get_db
    app.dependency_overrides[interviews_get_db] = override_get_db
    app.dependency_overrides[patients_get_db] = override_get_db
    app.dependency_overrides[questions_get_db] = override_get_db
    app.dependency_overrides[safety_get_db] = override_get_db
    app.dependency_overrides[sessions_get_db] = override_get_db
    app.dependency_overrides[summaries_get_db] = override_get_db
    app.dependency_overrides[timeline_get_db] = override_get_db

    app.dependency_overrides[security_get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()



@pytest.fixture
def db(db_session):
    return db_session