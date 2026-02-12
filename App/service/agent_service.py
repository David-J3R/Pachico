import os
import re
from dataclasses import dataclass, field
from typing import cast

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from App.MyAgent.graph import graph
from App.MyAgent.utils.state import INITIAL_SYSTEM_PROMPT, AgentState

_FILE_PATTERN = re.compile(r"exports[\\/][\w\-]+\.(?:png|csv)")


@dataclass
class AgentResponse:
    text: str
    file_paths: list[str] = field(default_factory=list)


def invoke_agent(user_input: str, thread_id: str) -> AgentResponse:
    """Invoke the LangGraph agent and return the final response."""
    config = RunnableConfig(configurable={"thread_id": thread_id})

    # Inject system prompt on first message of a thread
    existing_state = graph.get_state(config)
    messages: list = []

    if not existing_state.values.get("messages"):
        messages.append(INITIAL_SYSTEM_PROMPT)

    messages.append(HumanMessage(content=user_input))

    result = graph.invoke(cast(AgentState, {"messages": messages}), config=config)

    last_message = result["messages"][-1]
    text = last_message.content

    # Detect file paths in the full message history of this invocation
    file_paths: list[str] = []
    for match in _FILE_PATTERN.findall(text):
        normalized = match.replace("\\", "/")
        if os.path.isfile(normalized):
            file_paths.append(normalized)

    return AgentResponse(text=text, file_paths=file_paths)
