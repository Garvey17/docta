"""YOLO detector and Docta detection-response adapter."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ultralytics import YOLO


AI_SERVICES_DIR = Path(__file__).resolve().parent
DEFAULT_WEIGHTS_PATH = AI_SERVICES_DIR / "weights" / "best.pt"

# Only classes backed by a canonical nutrition profile are sent to the backend.
# Unmapped model classes are reported separately rather than guessed as another dish.
CLASS_TO_DISH: Dict[str, Tuple[str, str]] = {
    "akara": ("akara", "Akara"),
    "beef": ("beef", "Beef"),
    "egusi": ("egusi_soup", "Egusi Melon Seed Soup"),
    "fried rice": ("fried_rice", "Fried rice"),
    "jollof rice": ("jollof_rice", "Jollof rice"),
    "amala": ("amala", "Amala"),
    "efo": ("efo", "Efo"),
    "moi moi": ("moi_moi", "Moi moi"),
}


def _normalize_label(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def _class_name(names: Any, class_id: int) -> str:
    if isinstance(names, dict):
        return str(names.get(class_id, names.get(str(class_id), class_id)))
    return str(names[class_id])


def normalize_results(results: Iterable[Any], names: Any) -> Dict[str, List[Dict[str, Any]]]:
    """Convert YOLO pixel boxes into the normalized Docta detection contract."""
    detected_items: List[Dict[str, Any]] = []
    ignored_detections: List[Dict[str, Any]] = []

    for result in results:
        height, width = result.orig_shape
        boxes = result.boxes
        if boxes is None:
            continue

        for index, box in enumerate(boxes):
            class_id = int(box.cls[0].item())
            model_label = _class_name(names, class_id)
            match = CLASS_TO_DISH.get(_normalize_label(model_label))
            confidence = float(box.conf[0].item())
            xyxy = [float(value) for value in box.xyxy[0].tolist()]
            x_min, y_min, x_max, y_max = xyxy
            bounding_box = [
                max(0.0, min(1.0, x_min / width)),
                max(0.0, min(1.0, y_min / height)),
                max(0.0, min(1.0, x_max / width)),
                max(0.0, min(1.0, y_max / height)),
            ]

            if match is None:
                ignored_detections.append(
                    {
                        "model_label": model_label,
                        "confidence": confidence,
                        "bounding_box": bounding_box,
                        "reason": "No canonical nutrition profile is configured for this class.",
                    }
                )
                continue

            dish_id, display_name = match
            detected_items.append(
                {
                    "item_id": f"item_{len(detected_items) + 1}",
                    "predicted_dish_id": dish_id,
                    "display_name": display_name,
                    "confidence": confidence,
                    "bounding_box": bounding_box,
                }
            )

    return {"detected_items": detected_items, "ignored_detections": ignored_detections}


class DoctaObjectDetector:
    """Loads the trained YOLO model and exposes Docta-compatible predictions."""

    def __init__(self, weights_path: str | Path = DEFAULT_WEIGHTS_PATH, device: Optional[str] = None):
        self.weights_path = Path(weights_path).expanduser().resolve()
        if not self.weights_path.is_file():
            raise FileNotFoundError(f"Model weights not found at {self.weights_path}")
        self.model = YOLO(str(self.weights_path))
        self.device = device

    def predict(self, image_source: Any, conf_threshold: float = 0.5) -> List[Any]:
        """Run YOLO on one image path, URL, PIL image, or NumPy array."""
        if not 0.0 <= conf_threshold <= 1.0:
            raise ValueError("conf_threshold must be between 0 and 1")
        options: Dict[str, Any] = {"source": image_source, "conf": conf_threshold, "verbose": False}
        if self.device:
            options["device"] = self.device
        return self.model.predict(**options)

    def detect(self, image_source: Any, conf_threshold: float = 0.5) -> Dict[str, List[Dict[str, Any]]]:
        results = self.predict(image_source, conf_threshold=conf_threshold)
        return normalize_results(results, self.model.names)
