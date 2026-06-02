import pytest
import os
import backend.database as database

@pytest.fixture(autouse=True)
def setup_db():
    os.makedirs("outputs/charts", exist_ok=True)
    os.makedirs("data/cache", exist_ok=True)
    database.init_db()
    yield
