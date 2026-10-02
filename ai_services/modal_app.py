from pathlib import Path
import sys

import modal

AI_SERVICES_DIR = Path(__file__).resolve().parent

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install_from_requirements(str(AI_SERVICES_DIR / "requirements.txt"))
    .add_local_dir(str(AI_SERVICES_DIR), remote_path="/root/ai_services")
)

app = modal.App("docta-cv")


@app.function(image=image, timeout=120)
@modal.asgi_app(requires_proxy_auth=True)
def fastapi_app():
    sys.path.insert(0, "/root/ai_services")
    from app import app as fastapi_application
    return fastapi_application