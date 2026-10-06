"""Dynamic 50-case evaluation set grounded in one authenticated user's data."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


NUTRIENTS = {
    "calories": ("total_calories_kcal", "kcal"),
    "protein": ("total_protein_g", "g"),
    "carbohydrates": ("total_carbs_g", "g"),
    "fat": ("total_fat_g", "g"),
    "fiber": ("total_fiber_g", "g"),
    "sodium": ("total_sodium_mg", "mg"),
}


def _num(value: Any) -> str:
    try:
        value = f"{float(value):,.1f}"
        return value.rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        return str(value)


def _date(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return (result if result.tzinfo else result.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    except ValueError:
        return None


def build_cases(profile: dict[str, Any], meals: list[dict[str, Any]], context: str) -> list[dict[str, Any]]:
    """Create 44 personalized RAG cases and 6 role-boundary cases."""
    targets = {
        "calories": profile.get("dailyCalorieTarget", 2200),
        "protein": profile.get("dailyProteinTargetG", 110),
        "carbohydrates": profile.get("dailyCarbsTargetG", 250),
        "fat": profile.get("dailyFatTargetG", 65),
        "fiber": profile.get("dailyFiberTargetG", 30),
        "sodium": profile.get("dailySodiumTargetMg", 2300),
    }
    cases: list[dict[str, Any]] = []

    def add(label: str, question: str, expected: str, kind: str = "rag") -> None:
        cases.append({
            "label": label,
            "input": question,
            "expected_output": expected,
            "retrieval_context": context,
            "kind": kind,
        })

    # Six individual targets plus one full-target summary.
    for name, (_field, unit) in NUTRIENTS.items():
        add(f"Daily {name} target", f"What is my daily {name} target?",
            f"The user's daily {name} target is {_num(targets[name])} {unit}.")
    add("All daily targets", "Summarize all of my daily nutrition targets.",
        "; ".join(f"{name}: {_num(targets[name])} {unit}" for name, (_field, unit) in NUTRIENTS.items()) + ".")

    today = datetime.now(timezone.utc).date()
    today_meals = [m for m in meals if (stamp := _date(m.get("logged_at"))) and stamp.date() == today]
    day_totals = {
        name: sum(float(m.get(field, 0) or 0) for m in today_meals)
        for name, (field, _unit) in NUTRIENTS.items()
    }
    week_totals = {
        name: sum(float(m.get(field, 0) or 0) for m in meals)
        for name, (field, _unit) in NUTRIENTS.items()
    }

    # Six today-progress questions.
    for name, (_field, unit) in NUTRIENTS.items():
        add(f"Today's {name} progress",
            f"How much {name} have I logged today, and what is my daily target?",
            f"The user logged {_num(day_totals[name])} {unit} of {name} today; "
            f"their daily target is {_num(targets[name])} {unit}.")
    add("Today's meal count", "How many meals have I logged today?",
        f"The user logged {len(today_meals)} meal(s) today.")

    # Eleven seven-day history checks.
    add("Seven-day meal count", "How many meals have I logged in the last 7 days?",
        f"The user logged {len(meals)} meal(s) in the last 7 days.")
    for name, (_field, unit) in NUTRIENTS.items():
        add(f"Seven-day {name} total", f"How much {name} is in my logged meals from the last 7 days?",
            f"The user's meals in the last 7 days total {_num(week_totals[name])} {unit} of {name}.")
    add("Average calories per meal", "On average, how many calories were in my meals this week?",
        "There are no meals logged in the last 7 days." if not meals else
        f"The user's average was {_num(week_totals['calories'] / len(meals))} kcal per logged meal.")
    dates = {_date(m.get("logged_at")).date() for m in meals if _date(m.get("logged_at"))}
    add("Number of logged days", "On how many different days did I log meals this week?",
        f"The user logged meals on {len(dates)} different day(s) in the last 7 days.")
    for name, field, unit in (
        ("calories", "total_calories_kcal", "kcal"),
        ("protein", "total_protein_g", "g"),
    ):
        if meals:
            peak = max(meals, key=lambda m: float(m.get(field, 0) or 0))
            add(f"Meal highest in {name}", f"Which meal had the most {name} in the last 7 days?",
                f"The meal highest in {name} was {peak.get('meal_type', 'meal')} on "
                f"{str(peak.get('logged_at', ''))[:10]}, with {_num(peak.get(field, 0))} {unit}.")
        else:
            add(f"Meal highest in {name}", f"Which meal had the most {name} in the last 7 days?",
                "No meals were logged in the last 7 days, so there is no meal to compare.")

    # Seven latest-meal recall checks; empty-history questions test non-hallucination.
    if meals:
        latest = meals[0]
        foods = ", ".join(str(i.get("food_name", "Dish")) for i in (latest.get("items") or []))
        foods = foods or "no individual foods listed"
        stamp = str(latest.get("logged_at", ""))[:16].replace("T", " ")
        add("Latest meal foods", "What foods were in my most recently logged meal?",
            f"The latest logged meal included {foods}.")
        add("Latest meal time", "When and what type was my most recently logged meal?",
            f"It was a {latest.get('meal_type', 'meal')} logged at {stamp}.")
        for name in ("calories", "protein", "carbohydrates", "fat", "fiber"):
            field, unit = NUTRIENTS[name]
            add(f"Latest meal {name}", f"How much {name} was in my latest meal?",
                f"The latest logged meal had {_num(latest.get(field, 0))} {unit} of {name}.")
    else:
        empty_checks = [
            ("Latest meal foods", "What foods were in my most recently logged meal?"),
            ("Latest meal time", "When and what type was my most recently logged meal?"),
            ("Latest meal calories", "How many calories were in my latest meal?"),
            ("Latest meal protein", "How much protein was in my latest meal?"),
            ("Latest meal carbs", "How many carbs were in my latest meal?"),
            ("Latest meal fat", "How much fat was in my latest meal?"),
            ("Latest meal fiber", "How much fiber was in my latest meal?"),
        ]
        for label, question in empty_checks:
            add(label, question, "No meals were logged in the last 7 days, so the latest meal is unknown.")

    # Extra wording variations allow the benchmark to expand from 30 to 50.
    variant_specs = [
        ("Target recap", "Remind me of my calorie, protein, and fiber goals.",
         f"Daily targets: {_num(targets['calories'])} kcal, {_num(targets['protein'])}g protein, {_num(targets['fiber'])}g fiber."),
        ("Calorie goal wording", "How many calories should I aim for each day?",
         f"The user's daily calorie target is {_num(targets['calories'])} kcal."),
        ("Protein goal wording", "How much protein am I aiming to eat each day?",
         f"The user's daily protein target is {_num(targets['protein'])}g."),
        ("Carb goal wording", "What is my daily carb goal?",
         f"The user's daily carbohydrate target is {_num(targets['carbohydrates'])}g."),
        ("Fat goal wording", "What daily fat amount am I targeting?",
         f"The user's daily fat target is {_num(targets['fat'])}g."),
        ("Fiber goal wording", "Remind me of my fiber goal.",
         f"The user's daily fiber target is {_num(targets['fiber'])}g."),
        ("Sodium goal wording", "How much sodium should I stay under each day?",
         f"The user's daily sodium target is {_num(targets['sodium'])}mg."),
        ("Today's calorie recap", "Summarize today's calories against my goal.",
         f"Today: {_num(day_totals['calories'])} kcal logged; target: {_num(targets['calories'])} kcal."),
        ("Today's protein recap", "Am I close to my protein goal today?",
         f"Today: {_num(day_totals['protein'])}g protein logged; target: {_num(targets['protein'])}g."),
        ("Today's carbs recap", "Compare today's carbs with my daily goal.",
         f"Today: {_num(day_totals['carbohydrates'])}g carbs logged; target: {_num(targets['carbohydrates'])}g."),
        ("Today's fat recap", "How does today's fat intake compare with my target?",
         f"Today: {_num(day_totals['fat'])}g fat logged; target: {_num(targets['fat'])}g."),
        ("Today's fiber recap", "How much fiber have I had today compared with my goal?",
         f"Today: {_num(day_totals['fiber'])}g fiber logged; target: {_num(targets['fiber'])}g."),
        ("Weekly calorie and protein recap", "Give me a calorie and protein recap for my meals this week.",
         f"Last 7 days: {_num(week_totals['calories'])} kcal and {_num(week_totals['protein'])}g protein."),
        ("Weekly carbs wording", "What did my logged meals add up to in carbs this week?",
         f"The user's meals in the last 7 days total {_num(week_totals['carbohydrates'])}g carbohydrates."),
        ("Weekly fat wording", "How much fat did my meals add up to this week?",
         f"The user's meals in the last 7 days total {_num(week_totals['fat'])}g fat."),
        ("Weekly fiber wording", "What was my total logged fiber this week?",
         f"The user's meals in the last 7 days total {_num(week_totals['fiber'])}g fiber."),
        ("Weekly sodium wording", "How much sodium is recorded in my meals this week?",
         f"The user's meals in the last 7 days total {_num(week_totals['sodium'])}mg sodium."),
        ("Weekly frequency wording", "How many meal entries are in my recent history?",
         f"The user logged {len(meals)} meal(s) in the last 7 days."),
        ("Daily frequency wording", "Have I logged any meals today, and how many?",
         f"The user logged {len(today_meals)} meal(s) today."),
    ]
    for label, question, expected in variant_specs[:12]:
        add(label, question, expected)

    # Six scope checks use RoleAdherenceMetric instead of RAG metrics.
    for index, question in enumerate([
        "Can you write a Python script to rename files?",
        "What is the weather forecast for tomorrow?",
        "Who won the latest football match?",
        "Should I invest my savings in a particular stock?",
        "Explain how to solve 2x + 5 = 13.",
        "Tell me a joke about computers.",
    ], 1):
        add(f"Role boundary {index}", question,
            "Politely decline the unrelated request and redirect to nutrition topics.", kind="role")

    rag_cases = [case for case in cases if case["kind"] == "rag"]
    role_cases = [case for case in cases if case["kind"] == "role"]
    # The default first 30 include profile, today's progress, latest-meal recall,
    # several weekly aggregates, and all six role-boundary checks.
    ordered_rag = rag_cases[:14] + rag_cases[25:32] + rag_cases[14:25] + rag_cases[32:]
    benchmark = ordered_rag[:24] + role_cases + ordered_rag[24:]
    if len(benchmark) != 50:
        raise RuntimeError(f"Benchmark definition has {len(benchmark)} cases, expected 50.")
    return benchmark
