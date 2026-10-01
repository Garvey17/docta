# Docta food detection service

This service runs the trained YOLO model and exposes `POST /detect` for the backend.
It returns `detected_items` with normalized `[x_min, y_min, x_max, y_max]` boxes.
Classes without a configured nutrition profile are returned in `ignored_detections`.

## Install

From the project root in PowerShell:

```powershell
backend\.venv\Scripts\python.exe -m pip install -r ai_services\requirements.txt
```

The weights are stored at `ai_services/weights/best.pt`; the service finds them by
default. To use a different checkpoint, set `DOCTA_MODEL_WEIGHTS` to its path.
The minimum detection confidence defaults to `0.25`; set `DOCTA_CV_CONFIDENCE`
to a value from `0` to `1` to tune it.

## Run locally

Start the detector service from the project root:

```powershell
backend\.venv\Scripts\python.exe -m uvicorn ai_services.app:app --host 127.0.0.1 --port 8001
```

Point the backend at it in `backend/.env`:

```dotenv
CV_SERVICE_URL=http://127.0.0.1:8001
USE_MOCK_AI=false
```

Check `http://127.0.0.1:8001/health`, then submit a meal photo through the backend.
For image URLs, the service only fetches HTTPS addresses whose host is listed in
`DOCTA_ALLOWED_IMAGE_HOSTS` (comma-separated). Add the Supabase Storage host used
by the backend there when the CV service runs separately.

## Supported nutrition mappings

The model's Akara, Beef, Egusi, Fried Rice, Jollof-Rice, amala, efo, and moi-moi
classes map to existing backend dish IDs. Other model labels are surfaced as
ignored detections until the backend has a canonical nutrition profile for them.
The checkpoint metadata lists 17 classes, including an unexplained `a4` label;
the complete class metadata and evaluation metrics are not included with the
checkpoint, so the real-image checks are smoke tests rather than an accuracy
benchmark.

The checkpoint metadata identifies the model as AGPL-3.0 licensed. Review that
license against the project's intended deployment before distributing the model
or the service.
