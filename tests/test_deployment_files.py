from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_runs_migrations_before_api_start() -> None:
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text()

    assert "pip install --no-cache-dir -r requirements.txt" in dockerfile
    assert "alembic upgrade head" in dockerfile
    assert "uvicorn app.main:app --host 0.0.0.0 --port 8000" in dockerfile


def test_compose_defines_app_and_postgres_services() -> None:
    compose = (PROJECT_ROOT / "docker-compose.yml").read_text()

    assert "app:" in compose
    assert "build: ." in compose
    assert "postgres:" in compose
    assert "postgresql+psycopg://careermatch:careermatch@postgres:5432/careermatch" in compose
    assert "condition: service_healthy" in compose
    assert '"8000:8000"' in compose
