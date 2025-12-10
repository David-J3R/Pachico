from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    decision: Literal["food_entry", "data_review", "chart_request", "chatbot"]


# --- Router ---
class RouterChoice(BaseModel):
    step: Literal["food_entry", "data_review", "chart_request", "chatbot"] = Field(
        ...,
        description=(
            "food_entry: User mentions eating/consuming food\n"
            "data_review: User wants to review their history data (e.g., 'How many burgers I ate this week?')\n"
            "chart_request: User requests a chart/graph of their data (e.g., 'Show me a graph of my calorie intake this month')\n"
            "chatbot: General conversation"
        ),
    )
