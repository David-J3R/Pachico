import os
from typing import cast

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from .utils.checkpointer import memory
from .utils.nodes import (
    chart_request,
    chatbot,
    data_review,
    pick_node,
    router_node,
)
from .utils.state import INITIAL_SYSTEM_PROMPT, AgentState
from .utils.subgraph import subgraph as food_subgraph

builder = StateGraph(AgentState)

builder.add_node("router", router_node)
builder.add_node("chatbot", chatbot)
builder.add_node("food_entry", food_subgraph)
builder.add_node("data_review", data_review)
builder.add_node("chart_request", chart_request)


builder.add_edge(START, "router")
builder.add_conditional_edges(
    "router",
    pick_node,
)
builder.add_edge("food_entry", END)
builder.add_edge("data_review", END)
builder.add_edge("chart_request", END)
builder.add_edge("chatbot", END)

graph = builder.compile(checkpointer=memory)

# -------------------------------------------
# DRAW AND SAVE GRAPH
# -------------------------------------------
try:
    # Get the current working directory
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "Pachico_Graph.png")

    # Save the graph to a file
    png_data = graph.get_graph(xray=True).draw_mermaid_png()

    with open(file_path, "wb") as f:
        f.write(png_data)

    print("Graph saved as Pachico_Graph.png")
except Exception as e:
    print("Error saving graph:", e)

# -------------------------------------------
# EXAMPLE USAGE
# -------------------------------------------

config: RunnableConfig = {"configurable": {"thread_id": 1}}


def stream_graph_updates(user_input: str):
    # ~~~~~ Add Initial System Message ~~~~~
    existing_state = graph.get_state(config)
    messages = []

    if not existing_state.values.get("messages"):
        messages.append(INITIAL_SYSTEM_PROMPT)

    messages.append(HumanMessage(content=user_input))

    for event in graph.stream(
        cast(AgentState, {"messages": messages}),
        config=config,
    ):
        for value in event.values():
            # Check if 'messages' key exists in the value
            if value.get("messages"):
                print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except (EOFError, KeyboardInterrupt):
        # fallback if input() is not available
        print("An exit signal was received. Exiting the program.")
        break
