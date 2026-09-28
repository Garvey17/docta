-- ==============================================================================
-- docta Supabase PostgreSQL Database Schema
-- Complete schema supporting Authentication, Meals, Meal Items,
-- User Profiles, and "Log Everything" Active Learning Telemetry.
-- ==============================================================================

-- 1. Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. User Profiles Table (Mirrors or augments Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    name TEXT,
    daily_calorie_target INTEGER NOT NULL DEFAULT 2200,
    daily_protein_target_g NUMERIC NOT NULL DEFAULT 110.0,
    daily_carbs_target_g NUMERIC NOT NULL DEFAULT 250.0,
    daily_fat_target_g NUMERIC NOT NULL DEFAULT 65.0,
    daily_fiber_target_g NUMERIC NOT NULL DEFAULT 30.0,
    daily_sodium_target_mg NUMERIC NOT NULL DEFAULT 2300.0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_admin BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);

-- 3. Meals Table
CREATE TABLE IF NOT EXISTS public.meals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    image_url TEXT,
    meal_type TEXT NOT NULL DEFAULT 'lunch',
    notes TEXT,
    logged_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    total_calories_kcal NUMERIC NOT NULL DEFAULT 0.0,
    total_protein_g NUMERIC NOT NULL DEFAULT 0.0,
    total_fat_g NUMERIC NOT NULL DEFAULT 0.0,
    total_carbs_g NUMERIC NOT NULL DEFAULT 0.0,
    total_fiber_g NUMERIC NOT NULL DEFAULT 0.0,
    total_sodium_mg NUMERIC NOT NULL DEFAULT 0.0,
    total_calcium_mg NUMERIC NOT NULL DEFAULT 0.0,
    total_iron_mg NUMERIC NOT NULL DEFAULT 0.0
);

CREATE INDEX IF NOT EXISTS idx_meals_user_id ON public.meals(user_id);
CREATE INDEX IF NOT EXISTS idx_meals_logged_at ON public.meals(logged_at DESC);

-- 4. Meal Items Table
CREATE TABLE IF NOT EXISTS public.meal_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_id UUID NOT NULL REFERENCES public.meals(id) ON DELETE CASCADE,
    item_id TEXT,
    food_name TEXT NOT NULL,
    predicted_dish_id TEXT NOT NULL,
    final_dish_id TEXT NOT NULL,
    label_modified BOOLEAN NOT NULL DEFAULT false,
    confidence NUMERIC NOT NULL DEFAULT 1.0,
    bounding_box JSONB,
    selected_unit_id TEXT,
    selected_quantity NUMERIC NOT NULL DEFAULT 1.0,
    gram_weight NUMERIC NOT NULL DEFAULT 100.0,
    calories_kcal NUMERIC NOT NULL DEFAULT 0.0,
    protein_g NUMERIC NOT NULL DEFAULT 0.0,
    fat_g NUMERIC NOT NULL DEFAULT 0.0,
    carbs_g NUMERIC NOT NULL DEFAULT 0.0,
    fiber_g NUMERIC NOT NULL DEFAULT 0.0,
    sodium_mg NUMERIC NOT NULL DEFAULT 0.0,
    calcium_mg NUMERIC NOT NULL DEFAULT 0.0,
    iron_mg NUMERIC NOT NULL DEFAULT 0.0
);

CREATE INDEX IF NOT EXISTS idx_meal_items_meal_id ON public.meal_items(meal_id);

-- 5. "Log Everything" Active Learning Telemetry Table
-- Persists every CV prediction, bounding box, user label correction, selected unit,
-- and gram mass to build the ground-truth dataset for future automated ML training.
CREATE TABLE IF NOT EXISTS public.meal_item_feedback_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    meal_id UUID REFERENCES public.meals(id) ON DELETE CASCADE,
    meal_item_id UUID REFERENCES public.meal_items(id) ON DELETE CASCADE,
    image_url TEXT,
    predicted_dish_id TEXT NOT NULL,
    predicted_confidence NUMERIC NOT NULL DEFAULT 1.0,
    bounding_box JSONB,
    final_dish_id TEXT NOT NULL,
    label_modified BOOLEAN NOT NULL DEFAULT false,
    selected_unit_id TEXT NOT NULL,
    selected_quantity NUMERIC NOT NULL DEFAULT 1.0,
    calculated_gram_weight NUMERIC NOT NULL,
    custom_weight_entered_g NUMERIC,
    logged_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_feedback_logs_user_id ON public.meal_item_feedback_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_logs_meal_id ON public.meal_item_feedback_logs(meal_id);
CREATE INDEX IF NOT EXISTS idx_feedback_logs_logged_at ON public.meal_item_feedback_logs(logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_logs_predicted_dish ON public.meal_item_feedback_logs(predicted_dish_id);
CREATE INDEX IF NOT EXISTS idx_feedback_logs_final_dish ON public.meal_item_feedback_logs(final_dish_id);
CREATE INDEX IF NOT EXISTS idx_feedback_logs_label_modified ON public.meal_item_feedback_logs(label_modified);

-- 6. Row Level Security (RLS) Policies
ALTER TABLE public.meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.meal_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.meal_item_feedback_logs ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS automatically. For authenticated users:
CREATE POLICY "Users can manage their own profiles"
    ON public.user_profiles
    FOR ALL
    USING (auth.uid() = id);

CREATE POLICY "Users can manage their own meals"
    ON public.meals
    FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view meal items of their meals"
    ON public.meal_items
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.meals
            WHERE meals.id = meal_items.meal_id
            AND meals.user_id = auth.uid()
        )
    );
