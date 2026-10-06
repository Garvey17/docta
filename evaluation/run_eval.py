"""Run DeepEval checks against the authenticated Docta Insights API.

The script builds retrieval context and reference answers from the logged-in
user's profile and meals, then sends evaluation prompts to the running backend.
"""

from __future__ import annotations

import getpass
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=False)
load_dotenv(ROOT / "backend" / ".env", override=False)
load_dotenv(EVAL_DIR / ".env", override=False)

API_URL = os.getenv("DOCTA_API_URL", "http://127.0.0.1:8000").rstrip("/")
CHAT_PATH = "/api/v1/insights/chat"
ROLE = (
    "Docta's friendly, focused nutrition assistant. It answers questions about the user's "
    "food, meals, nutrition targets, calories, nutrients, hydration, and dietary wellness. "
    "It politely declines unrelated requests and does not invent personal meal or nutrition data."
)


def number(value: Any, digits: int = 1) -> str:
    """Format numeric values compactly for readable references."""
    try:
        rendered = f"{float(value):,.{digits}f}"
        return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered
    except (TypeError, ValueError):
        return str(value)


def parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def login(client: httpx.Client) -> str:
    """Use an existing bearer token or log in interactively without saving credentials."""
    token = os.getenv("DOCTA_ACCESS_TOKEN", "").strip()
    if token:
        return token

    email = input("Docta account email: ").strip()
    password = getpass.getpass("Docta account password: ")
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise RuntimeError("Login succeeded but the API did not return access_token.")
    return token


def build_context(profile: dict[str, Any], meals: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    """Mirror the profile and seven-day meal context used by the chat tool."""
    targets = {
        "calories": profile.get("dailyCalorieTarget", 2200),
        "protein": profile.get("dailyProteinTargetG", 110),
        "carbs": profile.get("dailyCarbsTargetG", 250),
        "fat": profile.get("dailyFatTargetG", 65),
        "fiber": profile.get("dailyFiberTargetG", 30),
        "sodium": profile.get("dailySodiumTargetMg", 2300),
    }
    target_text = (
        f"Daily Targets -> Calories: {number(targets['calories'])} kcal, "
        f"Protein: {number(targets['protein'])}g, Carbs: {number(targets['carbs'])}g, "
        f"Fat: {number(targets['fat'])}g, Fiber: {number(targets['fiber'])}g, "
        f"Sodium: {number(targets['sodium'])}mg"
    )

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    recent_meals = []
    for meal in meals:
        timestamp = parse_timestamp(meal.get("logged_at"))
        if timestamp and timestamp >= cutoff:
            recent_meals.append(meal)
    recent_meals = recent_meals[:30]

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    totals = {
        key: sum(float(meal.get(field, 0) or 0) for meal in recent_meals
                 if str(meal.get("logged_at", "")).startswith(today))
        for key, field in {
            "calories": "total_calories_kcal",
            "protein": "total_protein_g",
            "carbs": "total_carbs_g",
            "fat": "total_fat_g",
            "fiber": "total_fiber_g",
        }.items()
    }

    meal_lines = []
    for meal in recent_meals:
        foods = []
        for item in meal.get("items", []):
            foods.append(
                f"{item.get('food_name', 'Dish')} "
                f"({number(item.get('selected_quantity', 1))} "
                f"{item.get('selected_unit_id', 'portion')}, "
                f"{number(item.get('calories_kcal', 0))} kcal, "
                f"{number(item.get('protein_g', 0))}g protein)"
            )
        logged_at = str(meal.get("logged_at", ""))
        meal_lines.append(
            f"- [{logged_at[:16].replace('T', ' ')}] "
            f"{str(meal.get('meal_type', 'meal')).upper()}: "
            f"{number(meal.get('total_calories_kcal', 0))} kcal | "
            f"Protein: {number(meal.get('total_protein_g', 0))}g | "
            f"Carbs: {number(meal.get('total_carbs_g', 0))}g | "
            f"Fat: {number(meal.get('total_fat_g', 0))}g | "
            f"Fiber: {number(meal.get('total_fiber_g', 0))}g | "
            f"Sodium: {number(meal.get('total_sodium_mg', 0))}mg | "
            f"Foods: {', '.join(foods) if foods else 'No individual items recorded'}"
        )

    today_summary = (
        f"Today's Accumulated Totals ({today}):\n"
        f"• Calories: {number(totals['calories'])} / {number(targets['calories'])} kcal "
        f"(Remaining: {number(max(0, float(targets['calories']) - totals['calories']))} kcal)\n"
        f"• Protein: {number(totals['protein'])} / {number(targets['protein'])}g\n"
        f"• Carbs: {number(totals['carbs'])} / {number(targets['carbs'])}g\n"
        f"• Fat: {number(totals['fat'])} / {number(targets['fat'])}g\n"
        f"• Fiber: {number(totals['fiber'])} / {number(targets['fiber'])}g"
    )
    meals_summary = (
        "Logged Meals (Last 7 days, latest first):\n" + "\n".join(meal_lines)
        if meal_lines
        else "No logged meals found for this user in the past 7 days."
    )
    context = f"{target_text}\n\n{today_summary}\n\n{meals_summary}"
    return context, recent_meals


def chat(client: httpx.Client, question: str) -> tuple[str, float]:
    started = time.perf_counter()
    response = client.post(CHAT_PATH, json={"message": question, "history": []})
    response.raise_for_status()
    elapsed = time.perf_counter() - started
    reply = response.json().get("reply", "")
    return str(reply), elapsed


def build_judge():
    provider = os.getenv("DEEPEVAL_JUDGE", "openai").strip().lower()
    if provider == "ollama":
        from deepeval.models import OllamaModel

        return OllamaModel(
            model=os.getenv("DEEPEVAL_OLLAMA_MODEL", "qwen3:4b"),
            base_url=os.getenv("DEEPEVAL_OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0,
        )
    if provider != "openai":
        raise ValueError("DEEPEVAL_JUDGE must be 'openai' or 'ollama'.")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is required when DEEPEVAL_JUDGE=openai. "
            "Set DEEPEVAL_JUDGE=ollama to use the local Qwen judge instead."
        )
    return os.getenv("DEEPEVAL_MODEL", "gpt-4o-mini")


def run_metrics(
    rag_cases: list[dict[str, Any]],
    role_cases: list[dict[str, Any]],
    judge: Any,
) -> int:
    from deepeval.metrics import (
        AnswerRelevancyMetric,
        ContextualPrecisionMetric,
        ContextualRecallMetric,
        ContextualRelevancyMetric,
        FaithfulnessMetric,
        RoleAdherenceMetric,
    )
    from deepeval.test_case import ConversationalTestCase, LLMTestCase, Turn

    metrics_by_name = {
        "Answer relevancy": AnswerRelevancyMetric(threshold=0.7, model=judge, include_reason=True),
        "Faithfulness": FaithfulnessMetric(threshold=0.7, model=judge, include_reason=True),
        "Contextual relevancy": ContextualRelevancyMetric(threshold=0.7, model=judge, include_reason=True),
        "Contextual precision": ContextualPrecisionMetric(threshold=0.7, model=judge, include_reason=True),
        "Contextual recall": ContextualRecallMetric(threshold=0.7, model=judge, include_reason=True),
    }
    failures = 0
    for case in rag_cases:
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=case["actual_output"],
            expected_output=case["expected_output"],
            retrieval_context=[case["retrieval_context"]],
        )
        print(f"\n[{case['label']}] {case['input']}")
        print(f"Assistant: {case['actual_output']}")
        print(f"API latency: {case['latency']:.2f}s")
        for label, metric in metrics_by_name.items():
            try:
                metric.measure(test_case)
                score = float(metric.score)
                passed = score >= metric.threshold
                print(f"  {label}: {score:.2f} {'PASS' if passed else 'FAIL'}")
                if not passed:
                    failures += 1
                if getattr(metric, "reason", None):
                    print(f"    Reason: {metric.reason}")
            except Exception as error:
                failures += 1
                print(f"  {label}: ERROR ({error})")

    role_metric = RoleAdherenceMetric(threshold=0.8, model=judge, include_reason=True)
    for case in role_cases:
        role_test = ConversationalTestCase(
            chatbot_role=ROLE,
            turns=[
                Turn(role="user", content=case["input"]),
                Turn(role="assistant", content=case["actual_output"]),
            ],
        )
        print(f"\n[Role adherence: {case['label']}] {case['input']}")
        print(f"Assistant: {case['actual_output']}")
        print(f"API latency: {case['latency']:.2f}s")
        try:
            role_metric.measure(role_test)
            score = float(role_metric.score)
            passed = score >= role_metric.threshold
            print(f"  Role adherence: {score:.2f} {'PASS' if passed else 'FAIL'}")
            if getattr(role_metric, "reason", None):
                print(f"  Reason: {role_metric.reason}")
            if not passed:
                failures += 1
        except Exception as error:
            failures += 1
            print(f"  Role adherence: ERROR ({error})")

    return failures


def main() -> int:
    print(f"Docta Insights evaluation target: {API_URL}")
    try:
        question_count = int(os.getenv("EVAL_QUESTION_COUNT", "30"))
    except ValueError as error:
        raise ValueError("EVAL_QUESTION_COUNT must be 30 or 50.") from error
    if question_count not in {30, 50}:
        raise ValueError("EVAL_QUESTION_COUNT must be 30 or 50.")
    print(f"Running the {question_count}-question benchmark.")
    with httpx.Client(base_url=API_URL, timeout=180.0) as client:
        token = login(client)
        client.headers.update({"Authorization": f"Bearer {token}"})
        profile_response = client.get("/api/v1/profile")
        profile_response.raise_for_status()
        profile = profile_response.json()
        meals_response = client.get("/api/v1/meals", params={"page": 1, "page_size": 30})
        meals_response.raise_for_status()
        meals = meals_response.json().get("meals", [])

        retrieval_context, recent_meals = build_context(profile, meals)
        from benchmark import build_cases

        all_cases = build_cases(profile, recent_meals, retrieval_context)
        cases = all_cases[:question_count]
        print(
            f"Authenticated profile and meal history loaded. "
            f"{sum(case['kind'] == 'rag' for case in cases)} RAG cases, "
            f"{sum(case['kind'] == 'role' for case in cases)} role-boundary cases."
        )

        completed_cases = []
        for index, case in enumerate(cases, start=1):
            print(f"\nGenerating answer {index}/{question_count}: [{case['label']}] {case['input']}")
            answer, latency = chat(client, case["input"])
            completed_cases.append({**case, "actual_output": answer, "latency": latency})
    judge = build_judge()
    rag_cases = [case for case in completed_cases if case["kind"] == "rag"]
    role_cases = [case for case in completed_cases if case["kind"] == "role"]
    failures = run_metrics(rag_cases, role_cases, judge)
    print(f"\nEvaluation complete: {failures} metric(s) below threshold or errored.")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except httpx.HTTPStatusError as error:
        detail = error.response.text[:1000]
        print(f"API request failed ({error.response.status_code}): {detail}", file=sys.stderr)
        raise SystemExit(2)
    except httpx.RequestError as error:
        print(f"Could not reach {API_URL}: {error}", file=sys.stderr)
        raise SystemExit(2)
    except Exception as error:
        print(f"Evaluation could not start: {error}", file=sys.stderr)
        raise SystemExit(2)
