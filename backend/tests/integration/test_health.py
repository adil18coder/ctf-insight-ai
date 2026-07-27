import pytest


@pytest.mark.asyncio
async def test_liveness(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "app" in body


@pytest.mark.asyncio
async def test_readiness_reports_dependency_checks(client):
    # This hits real DB/Redis connections — in CI this runs against the
    # docker-compose services (Milestone 16 wires this into GitHub Actions).
    # Locally, run via `docker compose -f infra/docker-compose.dev.yml up`
    # first, or this will correctly report "degraded".
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert "checks" in body
    assert set(body["checks"].keys()) == {"database", "redis"}
