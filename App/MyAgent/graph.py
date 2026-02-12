from langgraph.graph import END, START, StateGraph

from .utils.chart_subgraph import chart_subgraph
from .utils.checkpointer import memory
from .utils.data_review_subgraph import data_review_subgraph
from .utils.nodes import (
    chatbot,
    pick_node,
    router_node,
)
from .utils.state import AgentState
from .utils.subgraph import subgraph as food_subgraph

builder = StateGraph(AgentState)

builder.add_node("router", router_node)
builder.add_node("chatbot", chatbot)
builder.add_node("food_entry", food_subgraph)
builder.add_node("data_review", data_review_subgraph)
builder.add_node("chart_request", chart_subgraph)


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
# try:
#     # Get the current working directory
#     current_dir = os.getcwd()
#     file_path = os.path.join(current_dir, "Pachico_Graph.png")

#     # Save the graph to a file
#     png_data = graph.get_graph(xray=True).draw_mermaid_png()

#     with open(file_path, "wb") as f:
#         f.write(png_data)

#     print("Graph saved as Pachico_Graph.png")
# except Exception as e:
#     print("Error saving graph:", e)
