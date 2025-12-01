"""
Automated tests for FastAPI server
Tests health checks, endpoints, and hot reload functionality
"""

import pytest
from fastapi.testclient import TestClient
from smart_customer_service.server import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_endpoint_exists(self, client):
        """Test that health endpoint is accessible"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        """Test health response has correct structure"""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "uptime_seconds" in data
        assert "config" in data
        assert "plugins" in data
        assert "timestamp" in data

    def test_health_status_healthy(self, client):
        """Test that status is healthy"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_uptime(self, client):
        """Test that uptime is reported"""
        response = client.get("/health")
        data = response.json()
        assert data["uptime_seconds"] >= 0

    def test_health_config_present(self, client):
        """Test that config is present in health check"""
        response = client.get("/health")
        data = response.json()
        assert "model" in data["config"]
        assert "temperature" in data["config"]


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestPluginsEndpoint:
    """Test plugins listing endpoint"""

    def test_list_plugins(self, client):
        """Test that plugins can be listed"""
        response = client.get("/plugins")
        assert response.status_code == 200
        data = response.json()
        assert "total_plugins" in data
        assert "plugins" in data


class TestOrdersEndpoint:
    """Test orders endpoint"""

    def test_list_orders(self, client):
        """Test that orders can be listed"""
        response = client.get("/orders")
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert "total" in data
        assert len(data["orders"]) > 0


class TestReloadEndpoint:
    """Test manual reload endpoint"""

    def test_trigger_reload(self, client):
        """Test manual reload trigger"""
        response = client.post("/reload")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "reloaded" in data
        assert "timestamp" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
