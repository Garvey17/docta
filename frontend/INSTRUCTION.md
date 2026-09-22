# Sub-Team 4 Directive: Mobile-First PWA & Dashboard UX

## 1. Directory Boundary & Autonomous Scope
> [!IMPORTANT]
> **Strict Directory Boundary**: As the Sub-Team 4 Autonomous Agent, you must operate strictly within `/subteam-4-frontend-ux/`. All backend API interactions must conform to the contracts specified in `/PROJECT_ORCHESTRATION.md`.

---

## 2. Directory Structure Tree

```
subteam-4-frontend-ux/
├── public/
│   ├── manifest.json                  # Web App Manifest for mobile PWA install
│   ├── sw.js                          # Service worker for offline caching
│   ├── icons/                         # App icon set (192x192, 512x512, maskable)
│   └── favicon.ico
├── src/
│   ├── app/                           # Next.js 14 App Router
│   │   ├── layout.tsx                 # Root layout with PWA meta & AuthProvider
│   │   ├── page.tsx                   # Daily Nutrition Dashboard view
│   │   ├── capture/
│   │   │   └── page.tsx               # Camera capture & prompt input view
│   │   ├── review/
│   │   │   └── page.tsx               # Bounding box review & portion editor
│   │   └── auth/
│   │       ├── login/page.tsx
│   │       └── signup/page.tsx
│   ├── components/
│   │   ├── CameraFeed.tsx             # HTML5 WebRTC live camera + fallback file picker
│   │   ├── BoundingOverlay.tsx        # Responsive HTML5 Canvas bounding box renderer
│   │   ├── PortionSlider.tsx          # Interactive gram weight slider (50g - 1000g)
│   │   ├── MacroProgressRing.tsx      # Calorie circular ring (Recharts/Chart.js)
│   │   ├── MacroBar.tsx               # Linear macro progress bars (Protein, Fat, Carbs)
│   │   ├── MealHistoryCard.tsx        # Collapsible card for previously logged meals
│   │   └── Navbar.tsx                 # Mobile bottom navigation bar
│   ├── hooks/
│   │   ├── useCamera.ts               # WebRTC stream controller & permission handler
│   │   ├── useAnalyzeMeal.ts          # Multipart POST hook to /api/v1/analyze
│   │   └── useDashboard.ts            # Daily summary fetcher & SWR/React Query cache
│   ├── store/
│   │   ├── authStore.ts               # Zustand store for JWT token & user profile
│   │   └── mealDraftStore.ts          # Zustand store for active analysis & edits
│   ├── types/
│   │   └── api.ts                     # TypeScript definitions matching backend contracts
│   └── lib/
│       ├── apiClient.ts               # Axios / Fetch client with auth interceptor
│       └── utils.ts                   # Formatting & calculation utilities
├── tests/
│   ├── CameraFeed.test.tsx
│   ├── BoundingOverlay.test.tsx
│   └── PortionSlider.test.tsx
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

---

## 3. Detailed Functional Requirements

### 3.1. Progressive Web App (PWA) Configuration
* **Manifest (`public/manifest.json`)**:
  * `name`: `"docta - Nigerian Nutrition Intelligence"`
  * `short_name`: `"docta"`
  * `display`: `"standalone"`
  * `orientation`: `"portrait"`
  * `background_color`: `"#0F172A"`
  * `theme_color`: `"#10B981"` (Emerald Green)
* **Service Worker (`public/sw.js`)**: Cache static assets and app shell for instant cold starts.

---

### 3.2. Camera Feed & Prompt Input (`CameraFeed.tsx`)
* Utilize WebRTC HTML5 `navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })`.
* Provide immediate fallback to native file input:
  `<input type="file" accept="image/*" capture="environment" />`
* Overlay interactive controls:
  * Shutter button to capture frame as JPEG blob.
  * Voice / Text Prompt input box (e.g. *"half wrap amala with 2 meats"*).
  * Loading state with animated pulse indicator while waiting for `/api/v1/analyze`.

---

### 3.3. Canvas Bounding Box Overlay (`BoundingOverlay.tsx`)
* Accept image source and array of detected items with normalized coordinates $[x_{\min}, y_{\min}, x_{\max}, y_{\max}] \in [0.0, 1.0]$.
* Dynamically map normalized coordinates to the rendered display dimensions:
  $$\text{Rendered } X = x_{\min} \times \text{canvas.width}$$
  $$\text{Rendered } Y = y_{\min} \times \text{canvas.height}$$
  $$\text{Rendered Width} = (x_{\max} - x_{\min}) \times \text{canvas.width}$$
  $$\text{Rendered Height} = (y_{\max} - y_{\min}) \times \text{canvas.height}$$
* Render stylized translucent boundary boxes with high-contrast colored borders and class badge tags (e.g., `"Jollof Rice - 272g"`).
* Enable tap-to-select: clicking a bounding box highlights the corresponding item in the portion editor list.

---

### 3.4. Interactive Meal Review & Portion Adjuster (`review/page.tsx`)
* Display detected food items in editable cards.
* **PortionSlider**: Provide a smooth slider control ($50\text{g}$ to $1000\text{g}$ with step $5\text{g}$) for each detected item.
* **Instant Macro Recalculation**: Adjusting the gram weight slider must instantly recalculate calories and macronutrients on the client side in real time using linear ratio scaling:
  $$\text{New Nutrient} = \left( \frac{\text{Baseline Nutrient}}{\text{Baseline Weight}} \right) \times \text{Adjusted Weight}$$
* "Confirm & Save Meal" button dispatches payload to `POST /api/v1/meals/log` and redirects to the dashboard.

---

### 3.5. Daily Macro Progress Dashboard (`app/page.tsx`)
* **Calorie Ring**: Render SVG / Recharts circular progress ring illustrating consumed vs. target daily calories and remaining allowance.
* **Macronutrient Bars**: Render 3 animated linear progress bars for:
  * Protein (g / target g)
  * Fats (g / target g)
  * Carbohydrates (g / target g)
* **Date Navigator**: Allow user to toggle between today and historical dates.
* **Logged Meals Feed**: Chronological list of logged meals (Breakfast, Lunch, Dinner) showing meal images, time, calorie badges, and itemized summaries.

---

## 4. TypeScript Interface Alignment

All API response parsing must conform to `src/types/api.ts`:

```typescript
export interface BoundingBox {
  xMin: number;
  yMin: number;
  xMax: number;
  yMax: number;
}

export interface NutrientBreakdown {
  caloriesKcal: number;
  proteinG: number;
  fatG: number;
  carbsG: number;
  fiberG: number;
  sodiumMg: number;
  calciumMg: number;
  ironMg: number;
}

export interface DetectedMealItem {
  itemId: string;
  dishId: string;
  displayName: string;
  confidence: number;
  boundingBox: [number, number, number, number]; // [x_min, y_min, x_max, y_max]
  weightG: number;
  wafctCode: string;
  nutrients: NutrientBreakdown;
}

export interface AnalyzeMealResponse {
  analysisId: string;
  status: string;
  imageUrl: string;
  detectedItems: DetectedMealItem[];
  totalNutrition: {
    totalCaloriesKcal: number;
    totalProteinG: number;
    totalFatG: number;
    totalCarbsG: number;
    totalFiberG: number;
    totalSodiumMg: number;
  };
}
```

---

## 5. Testing & Validation Commands

```bash
# 1. Install Sub-team 4 dependencies
npm install

# 2. Start Next.js development server
npm run dev

# 3. Run TypeScript typecheck & ESLint
npm run type-check
npm run lint

# 4. Run component unit tests
npm test

# 5. Build production bundle & verify PWA assets
npm run build
```

---

## 6. Definition of Done (DoD) Checklist

- [ ] Mobile PWA manifest and service worker load without errors in Lighthouse audit.
- [ ] `CameraFeed.tsx` streams live WebRTC video on mobile browsers and falls back cleanly to file upload.
- [ ] `BoundingOverlay.tsx` accurately draws bounding boxes over images across varying viewport aspect ratios.
- [ ] `PortionSlider.tsx` enables real-time client-side macro updates without UI stutter.
- [ ] Dashboard displays circular calorie ring and macro progress bars mapped to user targets.
- [ ] TypeScript strict mode passes with 0 type errors across the entire module.
- [ ] Jest / React Testing Library tests achieve $\ge 80\%$ test coverage.
