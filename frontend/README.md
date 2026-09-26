# docta Frontend: Mobile-First African Dietary Intelligence PWA

A high-performance, mobile-first Web & PWA frontend for **docta**, engineered specifically for African and Nigerian dietary compositions. It implements conventional portion sizing, multi-food localization, instant client-side macro scaling, and active learning decision telemetry logging.

The UI design system, layout, and component architecture strictly adhere to the clean, modern aesthetic of [Abdulrazak-Abdulsamad's Frontend Format](https://github.com/Abdulrazak-Abdulsamad/Funding-Ai-App): Inter typography, `#5B50E5` brand indigo accents, rounded-2xl cards with subtle borders, interactive score rings and progress gauges, responsive navigation (desktop right sidebar & mobile bottom bar), and full mock fallback support.

---

## 🌟 Key Features

1. **Daily Nutrition Dashboard (`DashboardScreen.jsx`)**:
   - Circular SVG Calorie Progress Ring (`MacroProgressRing.jsx`) tracking budget, consumed, and remaining calories.
   - 3 Summary KPI Cards (`NutritionSummaryCards.jsx`) for budget status, logged dishes, and active learning engine status.
   - Linear Macronutrient Progress Bars (`MacroBar.jsx`) for Protein, Carbohydrates, Healthy Fats, Dietary Fiber, and Sodium.
   - Logged Meals Timeline (`MealHistoryCard.jsx`) with dish tags and time-ago formatting.

2. **Multimodal Capture & Viewfinder (`CaptureScreen.jsx` & `CameraFeed.jsx`)**:
   - HTML5 WebRTC live camera stream with viewfinder reticle.
   - File drag-and-drop and image upload fallback.
   - Natural language context prompt (e.g., *"Party jollof with 2 extra fried plantains and peppered beef"*).
   - Quick demo samples (Jollof Rice + Plantain, Amala + Egusi Soup) for instant offline testing.

3. **Multi-Food Portion Review & Bounding Overlay (`ReviewScreen.jsx`)**:
   - **Responsive Canvas/SVG Localization Overlay (`BoundingOverlay.jsx`)**: Displays detected bounding boxes directly on the plate with synchronized hover and focus highlighting.
   - **Independent Food Item Cards (`FoodItemCard.jsx`)**: Rendered for every detected dish.
   - **Conventional Unit Selector (`PortionUnitSelector.jsx`)**: Culturally standard units (*Serving Spoon*, *Mound/Cup*, *Takeaway Pack*, *Wraps*, *Slices*) mapped directly from the Data/RAG registry.
   - **Interactive Quantity Steppers**: Increment/decrement buttons `[-] 2.0 [+]` with real-time recalculation.
   - **Predicted Label Override**: Searchable dropdown allowing users to correct misclassified foods; automatically sets `label_modified: true`.
   - **Instant Macro Recalculation**:
     $$\text{Item Weight (g)} = \text{Unit Gram Weight} \times \text{Quantity}$$
     $$\text{Item Nutrient} = \left(\frac{\text{Nutrient}_{\text{per 100g}}}{100.0}\right) \times \text{Item Weight}$$

4. **"Log Everything" Decision Telemetry Engine (`TelemetryModal.jsx`)**:
   - Compiles and audits all decisions according to `POST /api/v1/meals/log`:
     - `analysis_id`, `image_url`, `meal_type`, `logged_at`
     - Per-item: `predicted_dish_id`, `final_dish_id`, `label_modified`, `confidence`, `bounding_box`, `selected_unit_id`, `selected_quantity`, `gram_weight`, full nutrient breakdown.
   - Built-in Telemetry Inspector and Export utility for the ML team to train future automated volumetric weight models.

5. **PWA & Offline Capability**:
   - Web App Manifest (`manifest.json`) and Service Worker (`sw.js`) for standalone installability on iOS and Android.

---

## 🛠️ Tech Stack & Design System

- **Framework**: React 18 SPA + Vite
- **Styling**: Tailwind CSS (Inter font family, custom animations, `#5B50E5` brand palette)
- **Icons**: Lucide React
- **State Management**: Reactive store modules (`mealDraftStore.js`, `authStore.js`)
- **API Client**: Fetch wrapper with JWT interceptor and automatic mock fallback

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ (tested with Node.js v20.18.0)
- npm 9+

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Create `.env.local` (or copy from `.env.example`):
```env
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK=true
NEXT_PUBLIC_USE_MOCK=true
```
When `VITE_USE_MOCK=true`, the application operates completely autonomously without needing a live backend server or ML services.

### 3. Start Development Server
```bash
npm run dev
```
Opens at `http://localhost:3000`.

### 4. Run Test Suite
```bash
npm test
```
Executes automated tests validating portion unit scaling, nutrient formulas, and telemetry contract compliance.

### 5. Build for Production
```bash
npm run build
```
Generates optimized static bundle in `dist/`.

---

## 📂 Project Structure

```
frontend/
├── index.html                         # Entry HTML with PWA meta & Inter font
├── package.json                       # Dependencies & build scripts
├── vite.config.js                     # Vite configuration
├── tailwind.config.js                 # Tailwind CSS theme configuration
├── postcss.config.js                  # PostCSS plugins
├── public/
│   ├── manifest.json                  # PWA Web App Manifest
│   ├── sw.js                          # Service Worker
│   └── favicon.svg                    # SVG App Icon
├── src/
│   ├── main.jsx                       # React root entry point
│   ├── App.jsx                        # Application orchestrator & ErrorBoundary
│   ├── index.css                      # Tailwind base & custom keyframes
│   ├── api/
│   │   ├── apiClient.js               # HTTP client with auth headers
│   │   ├── mealApi.js                 # Analyze & log telemetry endpoints
│   │   └── authApi.js                 # JWT authentication service
│   ├── components/
│   │   ├── RightSidebar.jsx           # Desktop navigation sidebar
│   │   ├── Navbar.jsx                 # Mobile bottom navigation bar
│   │   ├── CameraFeed.jsx             # WebRTC live camera & file drop
│   │   ├── BoundingOverlay.jsx        # Responsive Canvas/SVG bounding boxes
│   │   ├── FoodItemCard.jsx           # Food card with label edit & unit picker
│   │   ├── PortionUnitSelector.jsx    # Conventional unit dropdown & stepper
│   │   ├── MacroProgressRing.jsx      # Calorie progress ring gauge
│   │   ├── MacroBar.jsx               # Linear macro progress bars
│   │   ├── NutritionSummaryCards.jsx  # Daily KPI summary cards
│   │   ├── MealHistoryCard.jsx        # Previously logged meal item cards
│   │   ├── TelemetryModal.jsx         # Telemetry inspector & ML export modal
│   │   ├── AuthModal.jsx              # Sign in & sign up modal
│   │   ├── CaptureScreen.jsx          # Capture & multimodal prompt view
│   │   ├── ReviewScreen.jsx           # Multi-food portion review view
│   │   └── DashboardScreen.jsx        # Daily nutrition dashboard view
│   ├── data/
│   │   ├── portionUnitsRegistry.js    # Conventional portion units from data_pipeline
│   │   └── mockData.js                # Deterministic Nigerian dishes and profiles
│   ├── store/
│   │   ├── authStore.js               # JWT & user state management
│   │   └── mealDraftStore.js          # Meal draft & telemetry payload builder
│   └── utils/
│       ├── macroCalculator.js         # Linear nutrient scaling algorithms
│       ├── scoreColors.js             # Color tokens & card styles
│       └── formatters.js              # Unit, calorie, and gram formatters
└── tests/
    └── macroCalculator.test.js        # Automated test suite
```
