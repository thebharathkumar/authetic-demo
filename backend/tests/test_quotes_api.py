from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


def test_quote_endpoint_returns_ranked_quotes():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    response = client.post(
        "/quotes",
        json={
            "age": 36,
            "zip_code": "94105",
            "state": "CA",
            "coverage_type": "auto",
            "household_income": 98000,
            "owns_home": False,
            "prior_claims": 1,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk"]["score"] > 0
    assert len(payload["quotes"]) == 4
    assert [quote["rank"] for quote in payload["quotes"]] == [1, 2, 3, 4]
    assert payload["best_quote"] == payload["quotes"][0]
