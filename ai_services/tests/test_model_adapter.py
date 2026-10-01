from ai_services.model import normalize_results


class Scalar:
    def __init__(self, value):
        self.value = value

    def item(self):
        return self.value


class Coordinates:
    def __init__(self, values):
        self.values = values

    def tolist(self):
        return self.values


class Box:
    def __init__(self, class_id, confidence, coordinates):
        self.cls = [Scalar(class_id)]
        self.conf = [Scalar(confidence)]
        self.xyxy = [Coordinates(coordinates)]


class Result:
    orig_shape = (100, 200)
    boxes = [
        Box(0, 0.91, [20, 10, 180, 90]),
        Box(1, 0.88, [0, 0, 100, 50]),
        Box(2, 0.77, [10, 20, 30, 40]),
    ]


def test_normalize_results_maps_supported_classes_and_normalizes_boxes():
    payload = normalize_results(
        [Result()],
        {0: "moi-moi", 1: "Fried Rice", 2: "a4"},
    )

    assert payload["detected_items"] == [
        {
            "item_id": "item_1",
            "predicted_dish_id": "moi_moi",
            "display_name": "Moi moi",
            "confidence": 0.91,
            "bounding_box": [0.1, 0.1, 0.9, 0.9],
        },
        {
            "item_id": "item_2",
            "predicted_dish_id": "fried_rice",
            "display_name": "Fried rice",
            "confidence": 0.88,
            "bounding_box": [0.0, 0.0, 0.5, 0.5],
        },
    ]
    assert payload["ignored_detections"][0]["model_label"] == "a4"

