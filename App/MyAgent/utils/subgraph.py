from langchain_core.messages import SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from App.MyAgent.clients.model import get_model

from .state import AgentState
from .tools import save_food_to_db, search_usda_foods

# Using default model and binding food-related tools
tools = [search_usda_foods, save_food_to_db]
food_model = get_model(temperature=0.4).bind_tools(tools)


def food_agent_node(state: AgentState):
    """
    Subgraph node for handling food_entries using a specialized food model with tools."""

    # When this subgraph node is invoked,
    # the last message must be always a food_entry request.

    system_msg = SystemMessage(
        content="""You are a helpful Nutrition assistant. Your goal is to accurately log the user's food intake.

## WORKFLOW (follow strictly):

### Step 1: Extract Information
- Extract the FOOD ITEM from the user's message
- Extract the QUANTITY (e.g., "2 eggs", "1 cup of rice", "150g chicken")
- If quantity is not specified, ask the user before proceeding

### Step 2: Search for Food Data
- Use 'search_usda_foods' with a concise food description
- Review the results carefully

### Step 3: Handle Search Results
**If results found:**
- Select the most relevant match
- Calculate nutrition based on the user's QUANTITY (not the default serving size)
- Present the food info to the user and ASK FOR CONFIRMATION before saving

**If NO results found (empty list):**
- Inform the user that the food wasn't found in USDA database
- Provide your best ESTIMATION of the nutritional values
- Clearly state it's an estimation and ASK FOR CONFIRMATION before saving

### Step 4: Save (ONLY after user confirms)
- Use 'save_food_to_db' with:
  - The user's specified quantity
  - source='usda' if from search, source='llm_estimation' if estimated
  - Accurate nutritional values adjusted for quantity

### Step 5: Confirm
- Tell the user the food has been logged with a summary

## IMPORTANT RULES:
- NEVER save without asking the user to confirm first
- ALWAYS adjust nutrition values based on user's quantity
- ALWAYS wait for search results before deciding next steps
- If user says "yes", "confirm", "ok", "save it" → proceed to save
- If user says "no", "cancel", "wrong" → ask what to change
""",
    )

    messages = [system_msg] + list(state["messages"])

    # Create a new message list with the system message and the food request
    response = food_model.invoke(messages)
    return {"messages": [response]}


usda_builder = StateGraph(AgentState)
usda_builder.add_node("food_agent", food_agent_node)
usda_builder.add_node("tools", ToolNode(tools))

usda_builder.add_edge(START, "food_agent")
usda_builder.add_conditional_edges("food_agent", tools_condition)
usda_builder.add_edge("tools", "food_agent")

subgraph = usda_builder.compile()
