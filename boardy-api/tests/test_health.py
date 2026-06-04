import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    # Проверяем только поле "ok", игнорируя остальные (гибкий тест)
    assert response.json()["ok"] is True
