# ML Engineer Guide: Food Identification Model Training & App Integration

## 1. Role & Architectural Pivot
> [!NOTE]
> **Audience**: This document is an **operational guide for the Machine Learning Engineer**. 
> All computer vision model training is conducted **manually by the ML Team**. Coding agents should NOT attempt automated training pipelines.
> 
> ### Key Architectural Pivot:
> * **Scope**: The vision model is trained **strictly on food identification and localization** (bounding box + multi-class classification).
> * **No Volumetric Weight Prediction**: Automated pixel-to-gram volumetric weight estimation has been removed from the vision model.
> * **Portion Resolution**: Portion sizes and gram weights are now resolved via a **Conventional Units of Measurement Lookup Table** on the application layer, where users select conventional units (e.g. *Serving Spoons*, *Wraps*, *Pieces*).
> * **Data Collection for Future Model**: All user selections and label corrections are logged by the backend to serve as the ground-truth training dataset for a future portion-size model.

---

## 2. Directory Structure Tree

```
ai_services/
├── data/
│   ├── raw/                           # Raw image dataset annotated with bounding boxes & class labels
│   ├── processed/                     # 640x640 processed images and YOLO label TXTs
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── dataset.yaml                   # YOLO dataset configuration
├── models/
│   ├── weights/
│   │   └── best.pt                    # [ML Hand-off] Trained YOLOv8/v11 PyTorch weights
│   ├── portion_units_lookup.json      # Conventional units registry & reference grams
│   └── yolo_config.yaml               # Hyperparameters used for manual training
├── src/
│   ├── __init__.py
│   ├── stub_predictor.py              # Dummy predictor for independent backend development
│   ├── pipeline.py                    # Master inference entrypoint connecting to Backend
│   ├── test_connection.py             # Validation script to verify model connection
│   └── schemas.py                     # Pydantic v2 data models
├── requirements.txt
└── INSTRUCTION.md
```

---

## 3. Dummy / Stub Mode for Independent Development

To allow the **Backend Team (`backend/`)** and **Frontend Team (`frontend/`)** to build authentication, portion selection cards, canvas bounding box overlays, and decision logging immediately:

### 3.1. Stub Predictor (`src/stub_predictor.py`)
When live weights are not yet generated or when `USE_STUB_PREDICTOR=true` is set:
```python
import time
from typing import Optional, List
from .schemas import VisionDetectionOutput, DetectedFoodItem

class StubPredictor:
    """Returns deterministic dummy detections for unblocked backend/frontend testing."""
    
    @staticmethod
    def predict(image_bytes: bytes, text_prompt: Optional[str] = None) -> VisionDetectionOutput:
        start_time = time.time()
        
        items = [
            DetectedFoodItem(
                dish_id="jollof_rice",
                display_name="Nigerian Jollof Rice",
                confidence=0.94,
                bounding_box=[0.125, 0.240, 0.550, 0.780]
            ),
            DetectedFoodItem(
                dish_id="fried_plantain",
                display_name="Fried Plantain (Dodo)",
                confidence=0.89,
                bounding_box=[0.580, 0.310, 0.890, 0.650]
            )
        ]
        
        duration_ms = (time.time() - start_time) * 1000 + 40.0
        return VisionDetectionOutput(
            detected_items=items,
            raw_prompt=text_prompt,
            processing_time_ms=round(duration_ms, 2)
        )
```

---

## 4. Manual Model Training Specifications (ML Team)

### 4.1. Target Food Identification Classes
Focus training on high-accuracy localization and classification for the initial target classes:
1. `jollof_rice` (Nigerian Jollof Rice)
2. `egusi_soup` (Egusi Melon Seed Soup)
3. `amala` (Yam Flour Swallow / Elubo)
4. `fried_plantain` (Dodo)
5. `moi_moi` (Steamed Bean Cake)
*(Additional classes: `suya`, `pounded_yam`, `eba`, `goat_meat`, `fried_fish`)*

### 4.2. Training Targets
* **Architecture**: Ultralytics YOLOv8m or YOLOv11m.
* **Resolution**: $640 \times 640$.
* **Performance Goal**: $\text{mAP50} \ge 0.88$ on food localization and multi-class classification.

---

## 5. How to Connect the Trained Model to the docta App

Follow these exact steps once manual model training is complete:

### Step 1: Copy Model Weights
Copy the final model checkpoint into the weights directory:
```bash
cp /path/to/your/trained/runs/detect/train/weights/best.pt ai_services/models/weights/best.pt
```

### Step 2: Implement the Inference Pipeline (`src/pipeline.py`)
Ensure `ai_services/src/pipeline.py` exposes the standard entrypoint used by the backend orchestrator:
```python
import os
from typing import Optional
from ultralytics import YOLO
from .schemas import VisionDetectionOutput, DetectedFoodItem
from .stub_predictor import StubPredictor

class FoodInferencePipeline:
    def __init__(self, weights_path: str = "models/weights/best.pt"):
        self.use_stub = os.getenv("USE_STUB_PREDICTOR", "false").lower() == "true"
        if not self.use_stub and os.path.exists(weights_path):
            self.model = YOLO(weights_path)
        else:
            self.model = None

    def analyze(self, image_bytes: bytes, text_prompt: Optional[str] = None) -> VisionDetectionOutput:
        if self.use_stub or self.model is None:
            return StubPredictor.predict(image_bytes, text_prompt)
        
        # Run YOLO inference
        results = self.model(image_bytes)
        detected_items = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxyn[0].tolist() # [x_min, y_min, x_max, y_max] normalized
            dish_name = self.model.names[cls_id]
            
            detected_items.append(DetectedFoodItem(
                dish_id=dish_name,
                display_name=dish_name.replace("_", " ").title(),
                confidence=round(conf, 3),
                bounding_box=xyxy
            ))
            
        return VisionDetectionOutput(
            detected_items=detected_items,
            raw_prompt=text_prompt,
            processing_time_ms=round(results[0].speed['inference'], 2)
        )
```

### Step 3: Verify Model Connection Standalone
```bash
python src/test_connection.py --image data/sample_meal.jpg
```

### Step 4: Notify Backend Team & Enable Live Mode
In `backend/.env`, set:
```env
USE_MOCK_AI=false
AI_MODEL_WEIGHTS_PATH="../ai_services/models/weights/best.pt"
```

---

## 6. Verification Checklist for ML Engineer

- [ ] `models/weights/best.pt` exists and is loadable by `ultralytics.YOLO`.
- [ ] Model outputs normalized bounding box coordinates $[x_{\min}, y_{\min}, x_{\max}, y_{\max}] \in [0.0, 1.0]$.
- [ ] `src/stub_predictor.py` runs and returns valid data when weights are absent.
- [ ] `python src/test_connection.py` runs successfully on test image.
