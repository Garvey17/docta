# Frontend Directive: Mobile-First PWA & Dashboard UX

## 1. Directory Boundary & Autonomous Scope
> [!IMPORTANT]
> **Strict Directory Boundary**: As the Frontend Agent, you must operate strictly within `/frontend/`. All API integrations and client data types must align with the canonical contracts defined in `/PROJECT_ORCHESTRATION.md`.

---

## 2. Directory Structure Tree

```
frontend/
├── public/
│   ├── manifest.json                  # Web App Manifest for mobile PWA install
│   ├── sw.js                          # Service worker for offline caching
│   ├── icons/                         # App icon set (192x192, 512x512, maskable)
│   └── dummy_meal.jpg                 # Sample placeholder image for offline mock review
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
│   │   ├── useAnalyzeMeal.ts          # Multipart POST hook with mock fallback
│   │   └── useDashboard.ts            # Daily summary fetcher with mock fallback
│   ├── store/
│   │   ├── authStore.ts               # Zustand store for JWT token & user profile
│   │   └── mealDraftStore.ts          # Zustand store for active analysis & edits
│   ├── types/
│   │   └── api.ts                     # TypeScript definitions matching backend contracts
│   └── lib/
│       ├── apiClient.ts               # Axios / Fetch client with auth interceptor
│       ├── mockData.ts                # Deterministic dummy responses for offline dev
│       └── utils.ts                   # Formatting & calculation utilities
├── tests/
│   ├── CameraFeed.test.tsx
│   ├── BoundingOverlay.test.tsx
│   └── PortionSlider.test.tsx
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── INSTRUCTION.md
```

---

## 3. Dummy / Mock Content Strategy for Independent Development

To enable the Frontend team and autonomous agents to design, build, and test the entire mobile PWA without requiring a running backend, database, or ML models:

### 3.1. Mock Configuration in `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK=true  # Set to false to connect to live backend
```

### 3.2. Static Mock Fixtures (`src/lib/mockData.ts`)
When `NEXT_PUBLIC_USE_MOCK=true`, the API client and custom hooks intercept network requests and return instant simulated responses after an artificial delay ($\sim 600\text{ms}$):

```typescript
import { AnalyzeMealResponse, DailyDashboardSummary } from '@/types/api';

export const MOCK_ANALYZE_RESPONSE: AnalyzeMealResponse = {
  analysisId: 'anlz_mock_001',
  status: 'success',
  processingDurationMs: 820.0,
  imageUrl: '/dummy_meal.jpg',
  detectedItems: [
    {
      itemId: 'item_1',
      dishId: 'jollof_rice',
      displayName: 'Nigerian Jollof Rice',
      confidence: 0.94,
      boundingBox: [0.125, 0.240, 0.550, 0.780],
      weightG: 272.0,
      wafctCode: '01_042',
      similarityScore: 0.942,
      isFallback: false,
      nutrients: {
        caloriesKcal: 380.8,
        proteinG: 7.3,
        fatG: 10.9,
        carbsG: 62.6,
        fiberG: 2.7,
        sodiumMg: 489.6,
        calciumMg: 21.8,
        ironMg: 1.9
      }
    },
    {
      itemId: 'item_2',
      dishId: 'fried_plantain',
      displayName: 'Fried Ripe Plantain (Dodo)',
      confidence: 0.89,
      boundingBox: [0.580, 0.310, 0.890, 0.650],
      weightG: 150.0,
      wafctCode: '02_018',
      similarityScore: 0.961,
      isFallback: false,
      nutrients: {
        caloriesKcal: 312.0,
        proteinG: 1.8,
        fatG: 14.1,
        carbsG: 48.0,
        fiberG: 3.6,
        sodiumMg: 6.0,
        calciumMg: 15.0,
        ironMg: 0.9
      }
    }
  ],
  totalNutrition: {
    totalCaloriesKcal: 692.8,
    totalProteinG: 9.1,
    totalFatG: 25.0,
    totalCarbsG: 110.6,
    totalFiberG: 6.3,
    totalSodiumMg: 495.6
  }
};
```

---

## 4. Detailed Component & UX Specifications

### 4.1. Camera Capture Feed (`CameraFeed.tsx`)
* Uses `navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })`.
* Provides immediate fallback to native file input: `<input type="file" accept="image/*" capture="environment" />`.
* Includes voice/text prompt override box (e.g. *"2 wraps of amala with extra meat"*).

### 4.2. Canvas Bounding Box Overlay (`BoundingOverlay.tsx`)
* Maps normalized ratios $[x_{\min}, y_{\min}, x_{\max}, y_{\max}] \in [0.0, 1.0]$ to rendered canvas pixels:
  $$\text{Rendered } X = x_{\min} \times \text{canvas.width}$$
  $$\text{Rendered } Y = y_{\min} \times \text{canvas.height}$$
  $$\text{Rendered Width} = (x_{\max} - x_{\min}) \times \text{canvas.width}$$
  $$\text{Rendered Height} = (y_{\max} - y_{\min}) \times \text{canvas.height}$$
* Renders bounding borders with pill badge overlays (e.g., `"Jollof Rice - 272g"`).
* Tapping a bounding box selects the corresponding item in the review list.

### 4.3. Interactive Review & Portion Slider (`review/page.tsx`)
* Provides interactive gram weight slider ($50\text{g} - 1000\text{g}$, step $5\text{g}$).
* Instantly recalculates calories and macros on the client side:
  $$\text{New Nutrient} = \left( \frac{\text{Baseline Nutrient}}{\text{Baseline Weight}} \right) \times \text{Adjusted Weight}$$
* "Log Meal" button posts payload to `/api/v1/meals/log` (or saves to mock store if in mock mode).

### 4.4. Dashboard Analytics (`app/page.tsx`)
* Circular progress ring displaying consumed vs. daily target calories.
* Linear progress bars for Protein, Fats, and Carbohydrates.
* Historical logged meal cards with thumbnails and calorie badges.

---

## 5. Testing & Validation Commands

```bash
# 1. Install dependencies
npm install

# 2. Start Next.js development server in Mock Mode
npm run dev

# 3. Run typecheck & linter
npm run type-check
npm run lint

# 4. Run component unit tests
npm test

# 5. Build production bundle
npm run build
```

---

## 6. Definition of Done (DoD) Checklist

- [ ] App launches and operates completely standalone in Mock Mode (`NEXT_PUBLIC_USE_MOCK=true`).
- [ ] `CameraFeed.tsx` streams live WebRTC video and captures snapshot blobs.
- [ ] `BoundingOverlay.tsx` accurately draws bounding boxes on meal images across responsive viewports.
- [ ] `PortionSlider.tsx` updates item and meal total macros in real time without lag.
- [ ] Dashboard displays calorie progress ring, macro bars, and meal history cards.
- [ ] Zero TypeScript errors and unit test coverage $\ge 80\%$.


---

## Automated Task Completion & Submission Protocol

When all functional requirements are implemented and local unit tests pass, execute the following submission sequence in the terminal:

### Step 1: Pre-Submission Health Check
Run the local test suite for your module. Do NOT push if any test fails.
* `pytest` (or `npm run build` for Frontend)

### Step 2: Automated Commit, Push & PR Creation
Execute these exact bash commands:

```bash
# 1. Switch to (or create) the dedicated sub-team branch
git checkout -B docta-frontend

# 2. Stage and commit changes
git add .
git commit -m "feat(docta-frontend): completed subteam task deliverables"

# 3. Push branch to GitHub
git push origin docta-frontend

# 4. Open Pull Request via GitHub CLI
gh pr create \
  --title "feat(docta-frontend): Completed Frontend Deliverables" \
  --body "Automated PR generated by Coding Agent upon completing INSTRUCTION.md tasks. All local tests passed." \
  --base main