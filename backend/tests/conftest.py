"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def client():
    """FastAPI test client."""
    from src.api.main import app
    return TestClient(app)


@pytest.fixture
def sample_customer_id():
    """Sample customer ID for testing."""
    return "test_cust_001"


@pytest.fixture
def sample_message():
    """Sample chat message."""
    return "I can't login to my account"
