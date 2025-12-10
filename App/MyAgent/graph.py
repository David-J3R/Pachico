import os
from typing import cast

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from .utils.checkpointer import memory
from .utils.nodes import (
    chart_request,
    chatbot,
    data_review,
    food_entry,
    pick_node,
    router_node,
)
from .utils.state import AgentState

builder = StateGraph(AgentState)

builder.add_node("router", router_node)
builder.add_node("chatbot", chatbot)
builder.add_node("food_entry", food_entry)
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
    for event in graph.stream(
        cast(AgentState, {"messages": [{"role": "user", "content": user_input}]}),
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
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
