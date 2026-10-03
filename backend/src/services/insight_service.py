"""Insight Service implementing an Agentic RAG Nutritionist Chatbot using LangChain and OpenAI."""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain.agents import create_agent

from ..config import get_settings
from ..supabase_client import get_supabase_client
from ..schemas.insight import ChatMessage

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert, compassionate certified clinical nutritionist and dietary coach for the docta nutrition application.
Your role is strictly to provide personalized dietary insights, nutritional analysis, meal advice, and healthy food recommendations based on the user's logged meals and nutrition history.

CRITICAL SCOPE RESTRICTIONS:
- You are acting solely as a professional nutritionist.
- You MUST NOT answer questions outside the scope of nutrition, food, diet, calories, macronutrients, micronutrients, hydration, and dietary wellness.
- If the user asks about ANY unrelated topic (for example: software programming, general trivia, politics, sports fixtures, finance, entertainment, movies, mathematics, or casual non-diet chit-chat), you MUST politely and firmly decline, explaining that you are a dedicated nutritionist and can only help with dietary and nutritional matters.

RETRIEVAL-AUGMENTED CONTEXT (RAG):
- You have access to database tools that query ONLY the current authenticated user's logged meals and nutrition profile targets.
- Whenever answering questions about what the user ate, their calories, protein, carbs, fats, remaining allowances, or tailored dietary recommendations, ALWAYS call the database tool to retrieve their real data as context.
- Ground your insights, calculations, and recommendations directly in this retrieved context.

NUTRITION GUIDANCE:
- Provide clear, actionable, encouraging advice.
- When suggesting meals, emphasize balanced, nutrient-dense foods. Where culturally relevant, incorporate West African / Nigerian dietary staples (e.g., steamed moi-moi, grilled fish/chicken, efo riro, okra soup, beans, brown rice, unripe plantain).
- Keep responses concise, well-structured, and easy to read using markdown bullet points and bold highlights.
"""


def _build_user_tools(user_id: str):
    """Build LangChain tools bound exclusively to the current user's ID."""

    @tool
    def get_user_nutrition_history(days: int = 7) -> str:
        """Retrieves the current user's logged meals, dishes, macronutrients (calories, protein, carbs, fat, fiber, sodium), and daily dietary targets from the database over the specified number of days (default 7). Use this tool whenever you need context on what the user ate or their nutritional progress."""
        supabase = get_supabase_client()

        # 1. Fetch user profile targets
        target_calories = 2200
        target_protein = 110.0
        target_carbs = 250.0
        target_fat = 65.0
        target_fiber = 30.0
        target_sodium = 2300.0

        try:
            prof_res = supabase.from_("user_profiles").select("*").eq("id", user_id).execute()
            if prof_res.data:
                p = prof_res.data[0]
                target_calories = p.get("daily_calorie_target") or p.get("dailyCalorieTarget") or target_calories
                target_protein = p.get("daily_protein_target_g") or p.get("dailyProteinTargetG") or target_protein
                target_carbs = p.get("daily_carbs_target_g") or p.get("dailyCarbsTargetG") or target_carbs
                target_fat = p.get("daily_fat_target_g") or p.get("dailyFatTargetG") or target_fat
                target_fiber = p.get("daily_fiber_target_g") or p.get("dailyFiberTargetG") or target_fiber
                target_sodium = p.get("daily_sodium_target_mg") or p.get("dailySodiumTargetMg") or target_sodium
        except Exception as e:
            logger.warning(f"Could not retrieve user profile targets: {e}")

        targets_str = (
            f"Daily Targets -> Calories: {target_calories} kcal, Protein: {target_protein}g, "
            f"Carbs: {target_carbs}g, Fat: {target_fat}g, Fiber: {target_fiber}g, Sodium: {target_sodium}mg"
        )

        # 2. Query logged meals for this user only
        try:
            query = supabase.from_("meals").select("*").eq("user_id", user_id).order("logged_at", desc=True)
            if days and days > 0:
                cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
                query = query.gte("logged_at", cutoff)

            meals_res = query.limit(30).execute()
            meals = meals_res.data or []
        except Exception as e:
            logger.error(f"Error querying meals for user {user_id}: {e}")
            return f"{targets_str}\nError retrieving logged meals from database."

        if not meals:
            return f"{targets_str}\n\nNo logged meals found for this user in the past {days} days."

        # 3. Format meals and calculate today's totals
        today_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_cals = 0.0
        today_prot = 0.0
        today_carbs = 0.0
        today_fat = 0.0
        today_fiber = 0.0

        meal_entries = []
        for m in meals:
            m_id = str(m.get("id"))
            logged_at = str(m.get("logged_at", ""))
            meal_type = m.get("meal_type", "meal")
            cal = float(m.get("total_calories_kcal", 0.0))
            prot = float(m.get("total_protein_g", 0.0))
            carb = float(m.get("total_carbs_g", 0.0))
            fat = float(m.get("total_fat_g", 0.0))
            fib = float(m.get("total_fiber_g", 0.0))
            sod = float(m.get("total_sodium_mg", 0.0))

            if logged_at.startswith(today_date_str):
                today_cals += cal
                today_prot += prot
                today_carbs += carb
                today_fat += fat
                today_fiber += fib

            # Fetch meal item details
            try:
                items_res = supabase.from_("meal_items").select("*").eq("meal_id", m_id).execute()
                items = items_res.data or []
                item_details = [
                    f"{it.get('food_name', 'Dish')} ({it.get('selected_quantity', 1)} {it.get('selected_unit_id', 'portion')}, {it.get('calories_kcal', 0)} kcal, {it.get('protein_g', 0)}g protein)"
                    for it in items
                ]
                items_str = ", ".join(item_details) if item_details else "No individual items recorded"
            except Exception:
                items_str = "Items unavailable"

            time_display = logged_at[:16].replace("T", " ")
            meal_entries.append(
                f"- [{time_display}] {meal_type.upper()}: {cal} kcal | Protein: {prot}g | Carbs: {carb}g | Fat: {fat}g | Fiber: {fib}g | Sodium: {sod}mg | Foods: {items_str}"
            )

        summary = (
            f"{targets_str}\n\n"
            f"Today's Accumulated Totals ({today_date_str}):\n"
            f"• Calories: {round(today_cals, 1)} / {target_calories} kcal (Remaining: {max(0, round(target_calories - today_cals, 1))} kcal)\n"
            f"• Protein: {round(today_prot, 1)} / {target_protein}g\n"
            f"• Carbs: {round(today_carbs, 1)} / {target_carbs}g\n"
            f"• Fat: {round(today_fat, 1)} / {target_fat}g\n"
            f"• Fiber: {round(today_fiber, 1)} / {target_fiber}g\n\n"
            f"Logged Meals (Last {days} days, latest first):\n"
            + "\n".join(meal_entries)
        )
        return summary

    @tool
    def get_user_nutrition_targets() -> str:
        """Retrieves the current user's profile nutritional targets (daily calorie target, protein, carbohydrates, fat, fiber, sodium). Use this tool when you need only the user's target goals."""
        supabase = get_supabase_client()
        try:
            prof_res = supabase.from_("user_profiles").select("*").eq("id", user_id).execute()
            if prof_res.data:
                p = prof_res.data[0]
                return (
                    f"User Targets -> "
                    f"Daily Calories: {p.get('daily_calorie_target') or p.get('dailyCalorieTarget', 2200)} kcal, "
                    f"Protein: {p.get('daily_protein_target_g') or p.get('dailyProteinTargetG', 110)}g, "
                    f"Carbohydrates: {p.get('daily_carbs_target_g') or p.get('dailyCarbsTargetG', 250)}g, "
                    f"Fat: {p.get('daily_fat_target_g') or p.get('dailyFatTargetG', 65)}g, "
                    f"Fiber: {p.get('daily_fiber_target_g') or p.get('dailyFiberTargetG', 30)}g, "
                    f"Sodium: {p.get('daily_sodium_target_mg') or p.get('dailySodiumTargetMg', 2300)}mg"
                )
        except Exception as e:
            logger.warning(f"Error fetching targets: {e}")
        return "Daily Targets: 2200 kcal, 110g protein, 250g carbs, 65g fat, 30g fiber, 2300mg sodium."

    return [get_user_nutrition_history, get_user_nutrition_targets]


class InsightService:
    """Service orchestrating the LangChain Agentic RAG Nutritionist Chatbot."""

    @classmethod
    async def chat(
        cls,
        user_id: str,
        message: str,
        history: Optional[List[ChatMessage]] = None,
    ) -> str:
        """Run the nutritionist agent for the authenticated user and return the response."""
        settings = get_settings()
        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        model_name = settings.openai_model or os.getenv("OPENAI_MODEL", "gpt-4o")

        if not api_key:
            return (
                "OpenAI API key is not configured. Please set the OPENAI_API_KEY environment "
                "variable to use the AI Nutritionist chatbot."
            )

        try:
            llm = ChatOpenAI(
                model=model_name,
                api_key=api_key,
                temperature=0.3,
            )

            # Build tools strictly scoped to this user_id
            tools = _build_user_tools(user_id=user_id)

            # Assemble conversation messages
            messages = []
            if history:
                for h in history[-8:]:  # keep last 8 messages for clean context window
                    if h.role == "user":
                        messages.append(HumanMessage(content=h.content))
                    elif h.role == "assistant":
                        messages.append(AIMessage(content=h.content))

            messages.append(HumanMessage(content=message))

            # Create agent with LangChain
            agent = create_agent(
                model=llm,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
            )

            response = await agent.ainvoke({"messages": messages})
            output_messages = response.get("messages", [])
            if output_messages:
                last_msg = output_messages[-1]
                return str(getattr(last_msg, "content", "") or "")

            return "I have reviewed your nutrition records. How else can I assist with your dietary goals today?"

        except Exception as e:
            logger.error(f"Error in InsightService.chat: {e}", exc_info=True)
            return (
                "I apologize, but I encountered an unexpected error analyzing your nutrition data. "
                "Please try again in a moment."
            )
