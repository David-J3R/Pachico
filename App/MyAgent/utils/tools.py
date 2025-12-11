from typing import Any, Dict, List, Literal, Optional

from langchain_core.tools import tool

from App.MyAgent.clients.usda_api import USDAClient

usda_client = USDAClient()


# --- USDA SEARCH TOOL ---
@tool
def search_usda_foods(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search USDA FoodData Central for food items.
    Returns a list of dictionaries matching foods with nutritional data.

    Args:
        query: Food description to search (e.g., "chicken breast", "banana")
               Keep it simple - just the food name, no quantities.
        limit: Max results (default: 5)

    Returns:
        List of dictonary food items with nutrition info, or empty list [] if not found.
        If empty, you should estimate the nutrition values instead.
    """
    results = usda_client.search_food(query, limit)

    if isinstance(results, list):
        return results
    return []


# ! NOT USED ANYMORE
# --- USDA SEARCH FOOD DETAILS TOOL ---
# @tool
# async def get_usda_food_details(fdc_id: int) -> Dict[str, Any]:
#     """
#     Get detailed portion information for a specific USDA food.
#     Args:
#         fdc_id: USDA FoodData Central ID
#     """
#     loop = asyncio.get_event_loop()
#     details = await loop.run_in_executor(None, usda_client.get_food_details, fdc_id)
#     return details if details and "error" not in details else {}


# --- USDA SAVE TOOL ---
@tool
def save_food_to_db(
    food_description: str,
    calories: float,
    protein_g: float,
    fat_g: float,
    carbs_g: float,
    quantity: float,
    unit: str,
    user_id: int = 1,
    fdc_id: Optional[int] = None,
    source: Literal["usda", "llm_estimation"] = "usda",
):
    """
    Saves the food item to the user's daily record.

    IMPORTANT: Only call this AFTER the user has confirmed the food entry!

    Args:
        food_description: Name of the food (e.g., "Chicken breast, grilled")
        calories: Total calories for the user's quantity
        protein_g: Protein in grams for the user's quantity
        fat_g: Fat in grams for the user's quantity
        carbs_g: Carbohydrates in grams for the user's quantity
        quantity: The amount the user consumed (e.g., 2, 1.5, 100)
        unit: Unit of measurement (e.g., "pieces", "grams", "cups", "oz")
        user_id: User identifier (default: 1)
        fdc_id: USDA FoodData Central ID (if from USDA search, otherwise None)
        source: "usda" if from database, "llm_estimation" if estimated

    Returns:
        "Success" if saved successfully
    """

    # Here you would connect to your SQL/NoSQL DB
    print(
        f"💾 SAVING: {food_description} | {calories} kcal | Protein: {protein_g}g | Fat: {fat_g}g | Carbs: {carbs_g}g | Quantity: {quantity} {unit} | User ID: {user_id} | FDC ID: {fdc_id} | Source: {source}"
    )
    return "Success"
