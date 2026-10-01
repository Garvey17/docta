"""Command-line runner for the Docta YOLO food detector."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence
from urllib.parse import urlparse

try:  # Supports both ``python -m ai_services.inference`` and direct execution.
    from .model import DEFAULT_WEIGHTS_PATH, DoctaObjectDetector, normalize_results
except ImportError:
    from model import DEFAULT_WEIGHTS_PATH, DoctaObjectDetector, normalize_results


def run_inference(
    image_path: str,
    weights_path: str | Path = DEFAULT_WEIGHTS_PATH,
    conf_threshold: float = 0.5,
    output_path: Optional[str | Path] = None,
) -> dict:
    detector = DoctaObjectDetector(weights_path=weights_path)
    results = detector.predict(image_path, conf_threshold=conf_threshold)
    detections = normalize_results(results, detector.model.names)

    if output_path:
        if len(results) != 1:
            raise RuntimeError(f"Expected one result for one image, got {len(results)}")
        save_path = Path(output_path).expanduser().resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        results[0].save(filename=str(save_path))
        detections["annotated_image"] = str(save_path)

    return detections


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Docta YOLO food detection on one image.")
    parser.add_argument("--image", required=True, help="Local image path or HTTP(S) image URL.")
    parser.add_argument(
        "--weights",
        default=str(DEFAULT_WEIGHTS_PATH),
        help="YOLO checkpoint (defaults to ai_services/weights/best.pt).",
    )
    parser.add_argument("--conf", type=float, default=0.5, help="Minimum confidence from 0 to 1.")
    parser.add_argument("--save", type=Path, help="Optional path for an annotated image.")
    args = parser.parse_args(argv)

    parsed_image = urlparse(args.image)
    is_http_url = parsed_image.scheme.lower() in {"http", "https"}
    if not is_http_url and not Path(args.image).is_file():
        parser.error(f"Image file does not exist: {args.image}")

    try:
        result = run_inference(args.image, args.weights, args.conf, args.save)
    except Exception as exc:
        parser.exit(1, f"Inference failed: {exc}\n")

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
