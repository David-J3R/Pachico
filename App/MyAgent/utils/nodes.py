from typing import Literal, cast

from App.MyAgent.clients.model import get_instructor, get_model

from .state import AgentState, RouterChoice

model = get_model()
# -------------------------------------------
# NODES
# -------------------------------------------


# --- ROUTER NODE ---
def router_node(state: AgentState):
    """
    A simple router node that decides the next step based on user input.
    """

    last_message = state["messages"][-1].content

    # Check if food_entry subgraph should continue waiting for confirmation
    if state.get("food_record_state") == "awaiting_confirmation":
        print("Router continuing to food_entry")
        return {"decision": "food_entry"}

    decision = cast(
        RouterChoice,
        get_instructor(message=last_message),
    )
    print(f"Router decision: {decision.step}")

    return {"decision": decision.step}


def pick_node(
    state: AgentState,
) -> Literal["food_entry", "data_review", "chart_request", "chatbot"]:
    return state["decision"]


# --- CHATBOT NODE ---
def chatbot(state: AgentState):
    answer = model.invoke(state["messages"])
    return {"messages": [answer]}


# # --- FOOD ENTRY NODE ---
# def food_entry(state: AgentState):
#     answer = model.invoke(state["messages"])
#     return {"messages": [answer]}
