import io

from fastapi.testclient import TestClient
from PIL import Image

from ai_services import app as app_module


class FakeDetector:
    def detect(self, image, conf_threshold):
        assert image.mode == "RGB"
        assert conf_threshold == 0.25
        return {
            "detected_items": [
                {
                    "item_id": "item_1",
                    "predicted_dish_id": "moi_moi",
                    "display_name": "Moi moi",
                    "confidence": 0.9,
                    "bounding_box": [0.1, 0.2, 0.8, 0.9],
                }
            ],
            "ignored_detections": [],
        }


def _image_bytes():
    stream = io.BytesIO()
    Image.new("RGB", (16, 12), color="orange").save(stream, format="JPEG")
    return stream.getvalue()


def test_detect_endpoint_accepts_image_upload(monkeypatch):
    monkeypatch.setattr(app_module, "_detector", FakeDetector())
    with TestClient(app_module.app) as client:
        response = client.post(
            "/detect",
            files={"file": ("moi-moi.jpg", _image_bytes(), "image/jpeg")},
        )

    assert response.status_code == 200
    assert response.json()["detected_items"][0]["predicted_dish_id"] == "moi_moi"


def test_detect_endpoint_rejects_non_image_upload(monkeypatch):
    monkeypatch.setattr(app_module, "_detector", FakeDetector())
    with TestClient(app_module.app) as client:
        response = client.post(
            "/detect",
            files={"file": ("not-an-image.txt", b"not an image", "text/plain")},
        )

    assert response.status_code == 415
