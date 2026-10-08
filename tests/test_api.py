from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Geospatial File Measurement API is running"
    }


def test_invalid_file_type():
    files = {
        "file": (
            "test.txt",
            b"This is not a geospatial file.",
            "text/plain"
        )
    }

    response = client.post(
        "/api/files/",
        files=files
    )

    assert response.status_code == 400


def test_file_not_found():
    response = client.get("/api/files/999999/")

    assert response.status_code == 404


def test_measurements_file_not_found():
    response = client.get(
        "/api/files/999999/measurements/"
    )

    assert response.status_code == 404