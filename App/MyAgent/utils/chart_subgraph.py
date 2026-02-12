from langchain_core.messages import SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from App.MyAgent.clients.model import get_model

from .state import AgentState
from .tools import generate_nutrition_chart

# Bind chart tools to the model
chart_tools = [generate_nutrition_chart]
chart_model = get_model(temperature=0.3).bind_tools(chart_tools)


def chart_agent_node(state: AgentState):
    """Subgraph node for generating nutrition charts using a specialized model with tools."""

    system_msg = SystemMessage(
        content="""You are Pachico's chart assistant. Your job is to generate nutrition timeline charts for users.

## WORKFLOW:

### Step 1: Parse the Request
- Identify which metric the user wants: calories, protein, fat, or carbs
- Identify the time period: weekly (last 7 days) or monthly (last 30 days)
- If the metric is not specified, default to "calories"
- If the period is not specified, default to "weekly"

### Step 2: Generate the Chart
- Call `generate_nutrition_chart` with the parsed metric and period
- ALWAYS generate the chart from real data — NEVER fabricate values

### Step 3: Respond
- Provide a brief summary of what the chart shows
- Include the file path of the generated chart image
- If the chart has all zeros, mention that no food entries were found for that period

## RULES:
- You are READ-ONLY. You cannot add, edit, or delete food entries.
- NEVER fabricate or hallucinate data. Always generate charts from real database entries.
- If the user asks for something outside of charting, politely explain you can only generate nutrition charts.
""",
    )

    messages = [system_msg] + list(state["messages"])
    response = chart_model.invoke(messages)

    return {"messages": [response]}


# Build the subgraph
chart_builder = StateGraph(AgentState)
chart_builder.add_node("chart_agent", chart_agent_node)
chart_builder.add_node("tools", ToolNode(chart_tools))

chart_builder.add_edge(START, "chart_agent")
chart_builder.add_conditional_edges("chart_agent", tools_condition)
chart_builder.add_edge("tools", "chart_agent")

chart_subgraph = chart_builder.compile()
