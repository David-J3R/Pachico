import csv
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from langchain_core.tools import tool
from sqlalchemy import Date
from sqlalchemy import cast as sa_cast

from App.database import FoodEntry, get_db_session
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
    meal_type: Optional[Literal["breakfast", "lunch", "dinner", "snack"]] = None,
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
        meal_type: Meal category if mentioned (breakfast, lunch, dinner, snack). Leave None if not specified.

    Returns:
        "Success" if saved successfully
    """
    entry = FoodEntry(
        user_id=user_id,
        food_description=food_description,
        calories=calories,
        protein_g=protein_g,
        fat_g=fat_g,
        carbs_g=carbs_g,
        quantity=quantity,
        unit=unit,
        fdc_id=fdc_id,
        source=source,
        meal_type=meal_type,
    )

    with get_db_session() as session:
        session.add(entry)

    print(
        f"💾 SAVED: {food_description} | {calories} kcal | {quantity} {unit} | meal: {meal_type}"
    )
    return "Success"


# -------------------------------------------
# DATA REVIEW TOOLS (read-only)
# -------------------------------------------


def _fetch_food_entries(
    user_id: int = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    meal_type: Optional[str] = None,
    food_keyword: Optional[str] = None,
) -> Dict[str, Any]:
    """Shared query logic for data review tools. Returns dict with summary, entries, count, totals."""

    with get_db_session() as session:
        query = session.query(FoodEntry).filter(FoodEntry.user_id == user_id)

        if start_date:
            query = query.filter(
                sa_cast(FoodEntry.created_at, Date)
                >= datetime.strptime(start_date, "%Y-%m-%d").date()
            )
        if end_date:
            query = query.filter(
                sa_cast(FoodEntry.created_at, Date)
                <= datetime.strptime(end_date, "%Y-%m-%d").date()
            )
        if meal_type:
            query = query.filter(FoodEntry.meal_type == meal_type)
        if food_keyword:
            query = query.filter(FoodEntry.food_description.ilike(f"%{food_keyword}%"))

        entries = query.order_by(FoodEntry.created_at.desc()).all()

        # list comprehension to convert SQLAlchemy objects to dicts for LLM consumption
        entry_list = [
            {
                "id": e.id,
                "food_description": e.food_description,
                "calories": e.calories,
                "protein_g": e.protein_g,
                "fat_g": e.fat_g,
                "carbs_g": e.carbs_g,
                "quantity": e.quantity,
                "unit": e.unit,
                "meal_type": e.meal_type,
                "source": e.source,
                "created_at": e.created_at.isoformat(),
            }
            for e in entries
        ]

    count = len(entry_list)
    totals = {
        "calories": round(sum(e["calories"] for e in entry_list), 1),
        "protein_g": round(sum(e["protein_g"] for e in entry_list), 1),
        "fat_g": round(sum(e["fat_g"] for e in entry_list), 1),
        "carbs_g": round(sum(e["carbs_g"] for e in entry_list), 1),
    }

    summary = f"Found {count} entries."

    return {
        "summary": summary,
        "entries": entry_list,
        "count": count,
        "totals": totals,
    }


@tool
def query_food_entries(
    user_id: int = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    meal_type: Optional[str] = None,
    food_keyword: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query the user's food log entries with optional filters. READ-ONLY.

    Args:
        user_id: User identifier (default: 1)
        start_date: Filter entries from this date (YYYY-MM-DD). If None, no lower bound.
        end_date: Filter entries up to this date (YYYY-MM-DD). If None, no upper bound.
        meal_type: Filter by meal type (breakfast, lunch, dinner, snack). If None, all meals.
        food_keyword: Search food descriptions containing this keyword (case-insensitive).

    Returns:
        Dict with summary text, list of entries (max 20), total count, and macro totals.
    """
    data = _fetch_food_entries(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        meal_type=meal_type,
        food_keyword=food_keyword,
    )
    # Cap entries at 20 for the LLM context window
    if data["count"] > 20:
        data["entries"] = data["entries"][:20]
        data["summary"] += " Showing the 20 most recent."
    return data


@tool
def export_food_csv(
    user_id: int = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    meal_type: Optional[str] = None,
    food_keyword: Optional[str] = None,
) -> str:
    """
    Export the user's food log entries to a CSV file with optional filters. READ-ONLY.

    Args:
        user_id: User identifier (default: 1)
        start_date: Filter entries from this date (YYYY-MM-DD). If None, no lower bound.
        end_date: Filter entries up to this date (YYYY-MM-DD). If None, no upper bound.
        meal_type: Filter by meal type (breakfast, lunch, dinner, snack). If None, all meals.
        food_keyword: Search food descriptions containing this keyword (case-insensitive).

    Returns:
        The file path of the exported CSV.
    """
    data = _fetch_food_entries(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        meal_type=meal_type,
        food_keyword=food_keyword,
    )

    if data["count"] == 0:
        return "No entries found matching the filters. Nothing to export."

    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(exports_dir, f"food_entries_{timestamp}.csv")

    fieldnames = [
        "id",
        "food_description",
        "calories",
        "protein_g",
        "fat_g",
        "carbs_g",
        "quantity",
        "unit",
        "meal_type",
        "source",
        "created_at",
    ]

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # Use _fetch_food_entries with no cap — entry_list already has all entries
        writer.writerows(data["entries"])

    return f"CSV exported successfully to: {file_path} ({data['count']} entries)"


# -------------------------------------------
# CHART TOOLS
# -------------------------------------------


@tool
def generate_nutrition_chart(
    metric: Literal["calories", "protein_g", "fat_g", "carbs_g"],
    period: Literal["weekly", "monthly"],
    user_id: int = 1,
) -> str:
    """
    Generate a bar chart of a nutrition metric over time and save it as a PNG image.

    Args:
        metric: The nutrition metric to chart — one of "calories", "protein_g", "fat_g", "carbs_g".
        period: Time range — "weekly" (last 7 days) or "monthly" (last 30 days).
        user_id: User identifier (default: 1).

    Returns:
        The file path of the generated chart image, or an error message if no data is found.
    """
    days = 7 if period == "weekly" else 30
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)

    data = _fetch_food_entries(
        user_id=user_id,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
    )

    # Group entries by date, summing the chosen metric per day
    daily_totals: Dict[str, float] = defaultdict(float)
    for entry in data["entries"]:
        entry_date = entry["created_at"][:10]  # string slicing: YYYY-MM-DD portion
        daily_totals[entry_date] += float(entry[metric])

    # Build continuous date range with zero-fill for missing days
    dates = []
    values = []
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        dates.append(current)
        values.append(round(daily_totals.get(date_str, 0.0), 1))
        current += timedelta(days=1)

    # Format labels and title
    metric_config = {
        "calories": {"label": "Calories (kcal)", "color": "#FF6B6B"},  # Coral red
        "protein_g": {"label": "Protein (g)", "color": "#4ECDC4"},  # Teal
        "fat_g": {"label": "Fat (g)", "color": "#FFE66D"},  # Yellow
        "carbs_g": {"label": "Carbs (g)", "color": "#A78BFA"},  # Purple
    }
    y_label = metric_config[metric]["label"]
    line_color = metric_config[metric]["color"]
    title = f"{y_label} — Last {days} Days"

    # Set up black background
    plt.style.use("dark_background")

    # Plot line chart
    fig, ax = plt.subplots(figsize=(12, 6), facecolor="#0D0D0D")  # Dark gray background
    ax.set_facecolor("#0D0D0D")  # Dark gray background for the plot area

    # Plot line chart with markers and gradient fill
    ax.plot(
        dates,
        values,
        color=line_color,
        linewidth=2.5,
        marker="o",
        markersize=6,
        markerfacecolor=line_color,
        markeredgecolor="#FFFFFF",
        markeredgewidth=1.5,
    )

    # Add subtle fill under the line
    ax.fill_between(dates, values, alpha=0.15, color=line_color)

    # Title and labels with modern font styling
    ax.set_title(
        title,
        fontsize=18,
        fontweight="bold",
        color="#FFFFFF",
        pad=20,
        fontfamily="sans-serif",
    )
    ax.set_xlabel("Date", fontsize=12, color="#AAAAAA", labelpad=10)
    ax.set_ylabel(y_label, fontsize=12, color="#AAAAAA", labelpad=10)

    # Style the grid
    ax.grid(axis="y", color="#333333", linestyle="--", linewidth=0.5, alpha=0.7)
    ax.grid(axis="x", color="#333333", linestyle="--", linewidth=0.5, alpha=0.3)

    # Style the spines (borders)
    for spine in ax.spines.values():
        spine.set_color("#333333")
        spine.set_linewidth(0.5)

    # Style tick labels
    ax.tick_params(axis="both", colors="#AAAAAA", labelsize=10)

    # Format x-axis dates
    fig.autofmt_xdate(rotation=45)

    # Add value annotations on data points (only for weekly to avoid clutter)
    if period == "weekly":
        for x, y in zip(dates, values):
            if y > 0:
                ax.annotate(
                    f"{y:.0f}",
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=9,
                    color="#FFFFFF",
                    fontweight="bold",
                )

    fig.tight_layout()

    # Save to exports/
    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(exports_dir, f"chart_{metric}_{period}_{timestamp}.png")
    fig.savefig(file_path, dpi=150, facecolor="#0D0D0D", edgecolor="none")
    plt.close(fig)

    # Reset style to default for other plots
    plt.style.use("default")

    return f"Chart saved to: {file_path}"
