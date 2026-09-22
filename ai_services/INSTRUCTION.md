# ML Engineer Guide: Model Training, Standalone Stubs & App Integration

## 1. Role & Purpose
> [!NOTE]
> **Audience**: This document is an **operational guide for the Machine Learning Engineer**. 
> All computer vision model training (dataset curation, bounding box labeling, hyperparameter tuning, and evaluation) is conducted **manually by the ML Team**. Coding agents should NOT attempt automated training pipelines.
> 
> This guide details:
> 1. The target specifications for manual model training.
> 2. How to provide dummy/stub predictions so the Backend and Frontend teams can develop without blocking on ML training.
> 3. Step-by-step instructions on **how to connect your trained model to the live docta backend** upon training completion.

---

## 2. Directory Structure Tree

```
ai_services/
├── data/
│   ├── raw/                           # Raw collected image dataset (10 Nigerian classes)
│   ├── processed/                     # 640x640 processed images and YOLO label TXTs
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── dataset.yaml                   # YOLO dataset configuration
├── models/
│   ├── weights/
│   │   └── best.pt                    # [ML Hand-off] Trained YOLOv8/v11 PyTorch weights
│   ├── portion_density.json           # Food item density and reference volume registry
│   └── yolo_config.yaml               # Hyperparameters used for manual training
├── src/
│   ├── __init__.py
│   ├── stub_predictor.py              # Dummy predictor for independent backend development
│   ├── volumetric_estimator.py        # Area-to-volume pixel-to-gram conversion
│   ├── multimodal_fusion.py           # Google GenAI (Gemini Flash) reasoning engine
│   ├── pipeline.py                    # Master inference entrypoint connecting to Backend
│   ├── test_connection.py             # Validation script to verify model connection
│   └── schemas.py                     # Pydantic v2 data models
├── requirements.txt
└── INSTRUCTION.md
```

---

## 3. Dummy / Stub Mode for Independent Development

To allow the **Backend Team (`backend/`)** and **Frontend Team (`frontend/`)** to build authentication, database logging, canvas bounding box overlays, and UI sliders immediately, `ai_services/` provides a **Stub Predictor** (`src/stub_predictor.py`).

### 3.1. How the Stub Predictor Works
When live model weights are not yet generated or when `USE_STUB_PREDICTOR=true` is set:
* `src/stub_predictor.py` immediately returns deterministic dummy detection payloads containing realistic bounding boxes, class names (`jollof_rice`, `fried_plantain`), and gram weights.
* If a text prompt is passed (e.g., *"3 pieces of dodo"*), the stub applies simulated override logic so downstream teams can verify text parsing.

### 3.2. Stub Implementation Pattern (`src/stub_predictor.py`)
```python
import time
from typing import Optional, Dict, Any
from .schemas import MultimodalVisionOutput, DetectedItem

class StubPredictor:
    """Returns deterministic dummy predictions for unblocked backend/frontend testing."""
    
    @staticmethod
    def predict(image_bytes: bytes, text_prompt: Optional[str] = None) -> MultimodalVisionOutput:
        start_time = time.time()
        
        # Simulated dummy items matching canonical contracts
        items = [
            DetectedItem(
                dish_id="jollof_rice",
                display_name="Nigerian Jollof Rice",
                confidence=0.94,
                bounding_box=[0.125, 0.240, 0.550, 0.780],
                estimated_volume_cm3=320.0,
                density_g_cm3=0.85,
                estimated_weight_g=272.0,
                text_override_applied=False,
                reasoning="Visual area estimation based on reference plate ratio."
            ),
            DetectedItem(
                dish_id="fried_plantain",
                display_name="Fried Plantain (Dodo)",
                confidence=0.89,
                bounding_box=[0.580, 0.310, 0.890, 0.650],
                estimated_volume_cm3=140.0,
                density_g_cm3=0.78,
                estimated_weight_g=150.0 if text_prompt and "dodo" in text_prompt.lower() else 109.2,
                text_override_applied=bool(text_prompt and "dodo" in text_prompt.lower()),
                reasoning="Text prompt specified portion override." if text_prompt and "dodo" in text_prompt.lower() else "Visual area heuristic."
            )
        ]
        
        duration_ms = (time.time() - start_time) * 1000 + 45.0  # Simulated inference latency
        return MultimodalVisionOutput(
            detected_items=items,
            raw_prompt=text_prompt,
            processing_time_ms=round(duration_ms, 2)
        )
```

---

## 4. Manual Model Training Specifications (ML Team)

### 4.1. 10 Target Nigerian Food Classes
Train the model on the following classes:
`jollof_rice`, `egusi_soup`, `amala`, `suya`, `pounded_yam`, `eba`, `fried_plantain`, `goat_meat`, `fried_fish`, `moi_moi`.

### 4.2. Training Targets
* **Architecture**: Ultralytics YOLOv8m or YOLOv11m.
* **Resolution**: $640 \times 640$.
* **Performance Goal**: $\text{mAP50} \ge 0.85$ across all 10 classes.
* **Volumetric Conversion Formula**:
  $$V_{\text{item}} (\text{cm}^3) = \left( \frac{A_{\text{box}}}{A_{\text{plate}}} \right) \times V_{\text{reference}} \times \text{depth\_factor}$$
  $$W_{\text{gram}} = V_{\text{item}} \times \text{density}$$

---

## 5. How to Connect the Trained Model to the docta App

Follow these exact steps once manual model training is complete:

### Step 1: Copy Model Weights
Copy the best model weights checkpoint into the weights directory:
```bash
cp /path/to/your/trained/runs/detect/train/weights/best.pt ai_services/models/weights/best.pt
```

### Step 2: Calibrate Food Density Values
Ensure `ai_services/models/portion_density.json` contains accurate densities and depth factors:
```json
{
  "jollof_rice": { "density_g_cm3": 0.85, "depth_factor": 1.0, "ref_serving_g": 250.0 },
  "egusi_soup": { "density_g_cm3": 1.05, "depth_factor": 0.8, "ref_serving_g": 200.0 },
  "amala": { "density_g_cm3": 1.15, "depth_factor": 1.1, "ref_serving_g": 300.0 },
  "suya": { "density_g_cm3": 0.70, "depth_factor": 0.5, "ref_serving_g": 150.0 },
  "pounded_yam": { "density_g_cm3": 1.20, "depth_factor": 1.1, "ref_serving_g": 350.0 },
  "eba": { "density_g_cm3": 1.10, "depth_factor": 1.0, "ref_serving_g": 300.0 },
  "fried_plantain": { "density_g_cm3": 0.78, "depth_factor": 0.6, "ref_serving_g": 150.0 },
  "goat_meat": { "density_g_cm3": 0.95, "depth_factor": 0.6, "ref_serving_g": 120.0 },
  "fried_fish": { "density_g_cm3": 0.88, "depth_factor": 0.6, "ref_serving_g": 180.0 },
  "moi_moi": { "density_g_cm3": 0.98, "depth_factor": 0.9, "ref_serving_g": 200.0 }
}
```

### Step 3: Implement the Inference Pipeline (`src/pipeline.py`)
Ensure `ai_services/src/pipeline.py` exposes the standard entrypoint used by the backend orchestrator:
```python
import os
from typing import Optional
from ultralytics import YOLO
from .schemas import MultimodalVisionOutput
from .volumetric_estimator import VolumetricEstimator
from .multimodal_fusion import GeminiMultimodalFusion
from .stub_predictor import StubPredictor

class FoodInferencePipeline:
    def __init__(self, weights_path: str = "models/weights/best.pt"):
        self.use_stub = os.getenv("USE_STUB_PREDICTOR", "false").lower() == "true"
        if not self.use_stub and os.path.exists(weights_path):
            self.model = YOLO(weights_path)
            self.volumetric = VolumetricEstimator("models/portion_density.json")
            self.fusion = GeminiMultimodalFusion(api_key=os.getenv("GEMINI_API_KEY"))
        else:
            self.model = None

    def analyze(self, image_bytes: bytes, text_prompt: Optional[str] = None) -> MultimodalVisionOutput:
        # Fallback to stub if model is missing or stub flag enabled
        if self.use_stub or self.model is None:
            return StubPredictor.predict(image_bytes, text_prompt)
        
        # 1. YOLO Object Detection
        # 2. Volumetric Weight Calculation
        # 3. Gemini Multimodal Fusion with text prompt overrides
        # Returns MultimodalVisionOutput
```

### Step 4: Verify Model Connection Standalone
Run the connection verification script to confirm weights, volumetric estimation, and Gemini API integration:
```bash
# Set Gemini API key
export GEMINI_API_KEY="your_api_key_here"

# Run integration test
python src/test_connection.py --image data/sample_meal.jpg --prompt "2 wraps of amala"
```

### Step 5: Notify Backend Team & Enable Live Mode
Inform the Backend Team that live weights are deployed. In `backend/.env`, set:
```env
USE_MOCK_AI=false
AI_MODEL_WEIGHTS_PATH="../ai_services/models/weights/best.pt"
```
The FastAPI backend orchestrator will automatically route live requests through your trained model.

---

## 6. Verification Checklist for ML Engineer

- [ ] `models/weights/best.pt` exists and is loadable by `ultralytics.YOLO`.
- [ ] `models/portion_density.json` has entries for all 10 classes.
- [ ] `src/stub_predictor.py` runs and returns valid data when weights are absent.
- [ ] `python src/test_connection.py` successfully returns normalized bounding boxes and gram weights.
- [ ] Gemini Flash fusion parses text prompt overrides correctly.
