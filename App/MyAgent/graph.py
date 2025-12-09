import os

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from .clients.model import get_model
from .utils.checkpointer import memory
from .utils.state import AgentState

model = get_model()


def chatbot(state: AgentState):
    answer = model.invoke(state["messages"])
    return {"messages": [answer]}


builder = StateGraph(AgentState)

builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile(checkpointer=memory)

# --- Draw a visual representation
try:
    # Get the current working directory
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "Agent_Graph.png")

    # Save the graph to a file
    png_data = graph.get_graph(xray=True).draw_mermaid_png()

    with open(file_path, "wb") as f:
        f.write(png_data)

    print("Graph saved as Agent_Graph.png")
except Exception as e:
    print("Error saving graph:", e)

# -------------------------------------------
# EXAMPLE USAGE
# -------------------------------------------

config: RunnableConfig = {"configurable": {"thread_id": 1}}


def stream_graph_updates(user_input: str):
    for event in graph.stream(
        {"messages": [{"role": "user", "content": user_input}]}, config=config
    ):
        for value in event.values():
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
