import instructor
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAI

from App.config import config
from App.MyAgent.utils.state import RouterChoice

template = """Question: {question}
Answer: Let's think step by step."""

prompt = PromptTemplate(template=template, input_variables=["question"])


def get_model(model_name: str = "amazon/nova-2-lite-v1:free", temperature: float = 0.7):
    """
    Returns a chat model instance connected to OpenRouter.
    You can change 'model_name' to any model on OpenRouter.
    """
    return ChatOpenAI(
        model=model_name,
        api_key=config.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=temperature,
    )


# For Instructor-based structured output
def get_instructor(model_name: str = "amazon/nova-2-lite-v1:free", message: str = ""):
    """
    Returns an Instructor model instance.
    You can change 'model_name' to any model supported by Instructor.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1", api_key=config.OPENROUTER_API_KEY
    )

    instructor_client = instructor.from_openai(client, mode=instructor.Mode.JSON)

    return instructor_client.chat.completions.create(
        model=model_name,
        response_model=RouterChoice,
        messages=[
            {
                "role": "system",
                "content": "You are a router. Classify the user input into the correct category.",
            },
            {"role": "user", "content": message},
        ],
    )


if __name__ == "__main__":
    # Test with a cheap model first
    llm = get_model()
    llm_chain = prompt | llm
    question = "Hello! Are you ready to track my calories?"

    print(llm_chain.invoke({"question": question}))
