# Frontend Directive: Mobile-First PWA, Multi-Food Portion Selector & Decision Telemetry UX

## 1. Directory Boundary & Autonomous Scope
> [!IMPORTANT]
> **Strict Directory Boundary**: As the Frontend Autonomous Agent, you must operate strictly within `/frontend/`. All API integrations, client state models, and telemetry payloads must strictly adhere to the schemas in `/PROJECT_ORCHESTRATION.md`.

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
│   │   │   └── page.tsx               # Multi-food review & conventional portion selector
│   │   └── auth/
│   │       ├── login/page.tsx
│   │       └── signup/page.tsx
│   ├── components/
│   │   ├── CameraFeed.tsx             # HTML5 WebRTC live camera + fallback file picker
│   │   ├── BoundingOverlay.tsx        # Responsive Canvas bounding box renderer
│   │   ├── FoodItemCard.tsx           # Card for each detected food (label edit + unit selector)
│   │   ├── PortionUnitSelector.tsx    # Dropdown of conventional units + quantity steppers
│   │   ├── MacroProgressRing.tsx      # Calorie circular ring (Recharts/Chart.js)
│   │   ├── MacroBar.tsx               # Linear macro progress bars (Protein, Fat, Carbs)
│   │   ├── MealHistoryCard.tsx        # Card for previously logged meals
│   │   └── Navbar.tsx                 # Mobile bottom navigation bar
│   ├── hooks/
│   │   ├── useCamera.ts               # WebRTC stream controller
│   │   ├── useAnalyzeMeal.ts          # Multipart POST hook with mock fallback
│   │   ├── useLogMeal.ts              # POST hook sending decisions + telemetry
│   │   └── useDashboard.ts            # Daily summary fetcher
│   ├── store/
│   │   ├── authStore.ts               # Zustand store for JWT & user profile
│   │   └── mealDraftStore.ts          # Zustand store for active multi-food analysis & user edits
│   ├── types/
│   │   └── api.ts                     # TypeScript definitions matching backend contracts
│   └── lib/
│       ├── apiClient.ts               # Axios / Fetch client with auth interceptor
│       ├── mockData.ts                # Deterministic dummy responses with portion units
│       └── utils.ts                   # Macro calculation utilities
├── tests/
│   ├── CameraFeed.test.tsx
│   ├── BoundingOverlay.test.tsx
│   ├── PortionUnitSelector.test.tsx
│   └── FoodItemCard.test.tsx
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── INSTRUCTION.md
```

---

## 3. Multi-Food Review & Conventional Portion Selector UX (`review/page.tsx`)

When `/api/v1/analyze` returns the recognized food items, the user is presented with the **Interactive Multi-Food Review Screen**:

### 3.1. Multi-Food Detection Support
If an image contains multiple dishes (e.g. *Nigerian Jollof Rice* and *Fried Plantain*), render an independent `FoodItemCard.tsx` for each detected item.

### 3.2. Conventional Portion Unit Selector (`PortionUnitSelector.tsx`)
Each food item card provides:
1. **Predicted Label with Editable Override**:
   * Displays the recognized name (e.g., *"Nigerian Jollof Rice"* with confidence pill `94%`).
   * Dropdown/Search allowing the user to correct the label if misidentified (automatically flags `label_modified: true`).
2. **Conventional Unit Dropdown**:
   * Displays culturally relevant units loaded from the API (e.g., `Serving Spoon (120g)`, `Mound / Cup (250g)`, `Takeaway Pack (500g)`).
3. **Quantity Stepper**:
   * Interactive increment/decrement buttons (`[-] 2.0 [+]` with step `0.5` or `1.0`).
4. **Instant Client-Side Macro Recalculation**:
   $$\text{Item Weight (g)} = \text{Unit Gram Weight} \times \text{Selected Quantity}$$
   $$\text{Item Calories} = \left( \frac{\text{Nutrient}_{\text{per 100g}}}{100.0} \right) \times \text{Item Weight}$$
   * Updates item subtotal and overall meal total in real-time as the user toggles units or changes quantity.

---

## 4. "Log Everything" Telemetry Payload

When the user taps **"Confirm & Log Meal"**, `useLogMeal` dispatches the full decision audit trail to `POST /api/v1/meals/log`:

```typescript
export interface LogMealItemPayload {
  itemId: string;
  foodName: string;
  predictedDishId: string;
  finalDishId: string;
  labelModified: boolean;
  confidence: number;
  boundingBox: [number, number, number, number];
  selectedUnitId: string;
  selectedQuantity: number;
  gramWeight: number;
  caloriesKcal: number;
  proteinG: number;
  fatG: number;
  carbsG: number;
  fiberG: number;
  sodiumMg: number;
  calciumMg: number;
  ironMg: number;
}
```

---

## 5. Mock Mode for Independent Frontend Development

In `.env.local`:
```env
NEXT_PUBLIC_USE_MOCK=true
```

When mock mode is enabled:
* `src/lib/mockData.ts` supplies mock multi-dish detections (Jollof Rice + Fried Plantain) with rich conventional units.
* The review screen, bounding box canvas, unit pickers, instant macro calculations, and dashboard update seamlessly without any running backend.

---

## 6. Testing & Validation Commands

```bash
# 1. Install dependencies
npm install

# 2. Start development server in Mock Mode
npm run dev

# 3. Run component tests (verifying unit selector & macro calculations)
npm test

# 4. Run TypeScript typecheck & ESLint
npm run type-check
npm run lint

# 5. Build production bundle
npm run build
```

---

## 7. Definition of Done (DoD) Checklist

- [ ] `FoodItemCard.tsx` renders conventional portion unit dropdowns and quantity steppers for every detected dish.
- [ ] Changing portion unit or quantity instantly updates the item and meal total macros in real-time.
- [ ] Users can edit/correct predicted dish labels with automatic `label_modified` flagging.
- [ ] Submitting a meal logs all decision telemetry fields (`predictedDishId`, `finalDishId`, `labelModified`, `selectedUnitId`, `selectedQuantity`, `gramWeight`).
- [ ] Zero TypeScript errors and unit test coverage $\ge 80\%$.