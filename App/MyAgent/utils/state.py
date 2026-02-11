from typing import Annotated, Literal, TypedDict

from langchain_core.messages import SystemMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

# --- INITIAL SYSTEM MESSAGE ---
INITIAL_SYSTEM_PROMPT = SystemMessage(
    content="""You are Pachico, a personal nutrition assistant. 
    Your role is to help users log their food intake, review their nutrition data, 
    and provide insights through charts.
    Your answers should be short, concise, and to the point.
    You can only answer nutrition and food related questions.
    your tone is like a friendly, funny, and professional nutritionist."""
)


# --- Agent State ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    decision: Literal["food_entry", "data_review", "chart_request", "chatbot"]
    food_record_state: Literal["awaiting_confirmation", None]


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
