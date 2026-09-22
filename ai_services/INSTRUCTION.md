# Sub-Team 1 Directive: Computer Vision & Multimodal AI Engine

## 1. Directory Boundary & Autonomous Scope
> [!IMPORTANT]
> **Strict Directory Boundary**: As the Sub-Team 1 Autonomous Agent, you must operate exclusively within `/subteam-1-cv-multimodal/`. You are prohibited from modifying files in other subteam directories. All outputs must conform to the canonical interfaces defined in `/PROJECT_ORCHESTRATION.md`.

---

## 2. Directory Structure Tree

```
subteam-1-cv-multimodal/
├── data/
│   ├── raw/                           # Raw collected image dataset (10 classes)
│   ├── processed/                     # 640x640 preprocessed & augmented images
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── dataset.yaml                   # YOLO dataset configuration
├── models/
│   ├── weights/
│   │   └── best.pt                    # Trained YOLOv8/v11 model weights
│   ├── portion_density.json           # Food item density and reference volume registry
│   └── yolo_config.yaml               # Hyperparameters for training
├── src/
│   ├── __init__.py
│   ├── dataset_preprocessor.py        # Albumentations pipeline & letterboxing
│   ├── train_yolo.py                  # Ultralytics training script
│   ├── volumetric_estimator.py        # Area-to-volume pixel-to-gram conversion
│   ├── multimodal_fusion.py           # Google GenAI (Gemini Flash) reasoning engine
│   ├── pipeline.py                    # Unified inference pipeline entrypoint
│   └── schemas.py                     # Pydantic v2 data models
├── tests/
│   ├── __init__.py
│   ├── test_preprocessor.py
│   ├── test_volumetric.py
│   ├── test_multimodal_fusion.py
│   └── test_pipeline.py
├── scripts/
│   ├── download_samples.py            # Fixture downloader for sample images
│   └── evaluate_metrics.py            # Precision, Recall, mAP50 evaluation
├── requirements.txt
└── README.md
```

---

## 3. Detailed Functional Requirements

### 3.1. Target Food Classes
The vision model detects 10 localized Nigerian culinary classes:
1. `jollof_rice` (Nigerian Jollof Rice)
2. `egusi_soup` (Egusi Melon Seed Soup)
3. `amala` (Yam Flour Paste)
4. `suya` (Spiced Skewered Beef)
5. `pounded_yam` (Iyan / Pounded Yam)
6. `eba` (Cassava Garri Swalllow)
7. `fried_plantain` (Dodo)
8. `goat_meat` (Asun / Stewed Goat Meat)
9. `fried_fish` (Fried Tilapia / Mackerel)
10. `moi_moi` (Steamed Bean Cake)

---

### 3.2. Preprocessing & Albumentations Augmentation
All training and inference images must undergo consistent preprocessing:
* Resizing with aspect-ratio preserving letterboxing to $640 \times 640 \times 3$.
* Albumentations Pipeline:
  * Random Rotation: $\pm 15^\circ$ ($p = 0.5$).
  * Horizontal Flip: $p = 0.5$.
  * Color Jitter (Brightness $\pm 20\%$, Contrast $\pm 20\%$, Saturation $\pm 15\%$).
  * Gaussian Blur: kernel size $(3, 3)$ ($p = 0.2$).
* Split distribution: 70% Train, 20% Validation, 10% Test.

---

### 3.3. YOLO Model Training
* Architecture: Ultralytics YOLOv8m or YOLOv11m.
* Training constraints:
  * Image size: $640$
  * Batch size: $16$ (or $32$ depending on GPU memory)
  * Epochs: $\ge 100$ with early stopping (patience = 15)
  * Optimizer: `AdamW`, learning rate $\text{lr0} = 0.001$, cosine LR scheduler.
* Metric Target: $\text{mAP50} \ge 0.85$ across all 10 classes.
* Output Artifact: Save optimal model weights to `models/weights/best.pt`.

---

### 3.4. Volumetric Pixel-to-Gram Estimator
Calculate volumetric mass through plate-relative surface area estimation:

1. **Normalized Box Area Calculation**:
   $$A_{\text{box}} = (x_{\max} - x_{\min}) \times (y_{\max} - y_{\min}) \times (640 \times 640)$$

2. **Reference Plate Area Ratio**:
   Assume standard circular or square dinner plate diameter occupies $A_{\text{plate}} = 600 \times 600 = 360,000\text{ px}^2$.
   $$\text{Area Ratio } R = \frac{A_{\text{box}}}{A_{\text{plate}}}$$

3. **Volumetric Estimation**:
   Given reference serving volume $V_{\text{reference}}$ (standardized to $450\text{ cm}^3$ for a full plate mound):
   $$V_{\text{item}} (\text{cm}^3) = R \times V_{\text{reference}} \times \text{depth\_factor}$$
   *(where $\text{depth\_factor}$ is $1.0$ for mounded swallow/rice, $0.6$ for flat meats/plantains, $0.8$ for soups).*

4. **Gram Weight Calculation**:
   Using localized food density $\rho$ loaded from `models/portion_density.json`:
   $$W_{\text{estimated}} (\text{g}) = V_{\text{item}} \times \rho$$

#### Food Density Registry (`models/portion_density.json`)
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

---

### 3.5. Multimodal Vision-Text Fusion via Gemini Flash
Integrate `google-genai` SDK using Gemini Flash (`gemini-2.5-flash` or `gemini-1.5-flash`).

#### Multimodal Reasoning Protocol:
1. **Inputs**:
   * Raw user image (Base64 / bytes).
   * YOLO detected bounding boxes with preliminary labels and visual weights.
   * Optional user text prompt (e.g., *"2 big wraps of amala with half bowl egusi and 3 pieces of goat meat"*).
2. **Override Logic**:
   * If the user explicitly mentions piece counts, portion fractions, or specific weight (e.g., *"3 pieces of goat meat"*, *"half wrap"*), the text prompt **strictly overrides** the visual area estimate.
   * If no text prompt is provided or if the prompt is generic (e.g., *"my lunch"*), use the CV volumetric calculated gram weight.
   * Flag each item with `text_override_applied: boolean`.
3. **Structured Response Constraint**: Enforce JSON output format using Gemini Structured Outputs.

---

## 4. Input & Output Contracts

### 4.1. Python Calling Interface (`Pipeline.analyze`)
```python
from pydantic import BaseModel
from typing import List, Optional

class DetectedItem(BaseModel):
    dish_id: str
    display_name: str
    confidence: float
    bounding_box: List[float]  # [x_min, y_min, x_max, y_max] normalized (0.0 - 1.0)
    estimated_volume_cm3: float
    density_g_cm3: float
    estimated_weight_g: float
    text_override_applied: bool
    reasoning: str

class MultimodalVisionOutput(BaseModel):
    detected_items: List[DetectedItem]
    raw_prompt: Optional[str] = None
    processing_time_ms: float
```

---

## 5. Testing & Validation Commands

```bash
# 1. Install Sub-team 1 dependencies
pip install -r requirements.txt

# 2. Run data preprocessor & verify 640x640 output
python src/dataset_preprocessor.py --input data/raw --output data/processed

# 3. Train YOLO model
python src/train_yolo.py --epochs 100 --batch 16 --data data/dataset.yaml

# 4. Evaluate mAP50 performance
python scripts/evaluate_metrics.py --weights models/weights/best.pt --data data/dataset.yaml

# 5. Run full unit and integration test suite
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## 6. Definition of Done (DoD) Checklist

- [ ] `data/processed/` generates valid $640 \times 640$ images and YOLO format labels.
- [ ] `train_yolo.py` successfully executes and saves weights to `models/weights/best.pt`.
- [ ] Model achieves $\text{mAP50} \ge 0.85$ across all 10 Nigerian food classes.
- [ ] `volumetric_estimator.py` converts bounding box coordinates and density into gram weights matching test benchmarks within $\pm 10\%$.
- [ ] `multimodal_fusion.py` connects to Gemini Flash and correctly parses user text overrides into structured JSON.
- [ ] `pytest tests/` runs with 100% pass rate and $\ge 85\%$ test coverage.
