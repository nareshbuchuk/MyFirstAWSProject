import io
from fastapi.testclient import TestClient
from app.main import app

def test_upload_file(monkeypatch):
    client = TestClient(app)
    def mock_upload_file_to_s3(file_obj, filename):
        return True
    monkeypatch.setattr("app.s3_client.upload_file_to_s3", mock_upload_file_to_s3)
    response = client.post("/upload", files={"file": ("test.txt", io.BytesIO(b"data"), "text/plain")})
    assert response.status_code == 200
    assert response.json()["message"].startswith("Uploaded")
