from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, SystemMessage

from .config import BEDROCK_MODEL_ID, AWS_REGION
from .retriever import get_retriever
from .state import AssistantState

def retrieve_node(state: AssistantState) -> dict:
    """ Retrieve documents using the current search query. """

    retriever = get_retriever()

    query = state["query"]
    if state["attempts"] == 0 and len(state["messages"]) > 1:
        prior = state["messages"][-2].content
        query = f"{prior} {query}"

    documents = retriever.invoke(query)

    return {
        "documents": documents,
        "attempts": state["attempts"] + 1,
    }


def grade_node(state: AssistantState) -> dict:
    """ Determine whether the retrieved documents support the question."""

    if not state["documents"]:
        return {"supported": False}

    context = "\n\n".join(
        f"Source: {document.metadata.get('source', 'unknown')}\n"
        f"{document.page_content}"
        for document in state["documents"]
    )

    model = ChatBedrockConverse(
        model_id=BEDROCK_MODEL_ID,
        region_name=AWS_REGION
    )

    prompt = f"""
        You are checking whether retrieved documents contain enough information
        to answer a user's question.

        Question: {state["question"]}
        Retrieved documents: {context}

        Decide whether the retrieved documents directly support an answer.
        Respond with exactly one word: YES or NO
            """

    response = model.invoke([HumanMessage(content=prompt)])

    supported = response.content.strip().upper() == "YES"

    return {
        "supported": supported
    }


def retry_node(state: AssistantState) -> dict:
    """ Create a broader query for the second retrieval attempt."""

    return {
        "query": f'{state["question"]} policy requirements details'
    }


def answer_node(state: AssistantState) -> dict:
    """ Generate an answer using the retrieved documents."""

    context = "\n\n".join(
        f"Source: {document.metadata.get('source', 'unknown')}\n"
        f"{document.page_content}"
        for document in state["documents"]
    )

    model = ChatBedrockConverse(
        model_id=BEDROCK_MODEL_ID,
        region_name=AWS_REGION
    )
    
    system_prompt = """
        You are a policy assistant.
        Answer the user's question using ONLY the provided retrieved documents.

        Do not use outside knowledge.
        Do not make up information.

        Cite the source document name after each relevant part of your answer.
        If the documents do not contain enough information to answer the question,
        say that the you could not find the information.
                    """

    history = state["messages"][:-1] 
    
    prompt = f"""
        User question: {state["question"]}
        Retrieved documents: {context}
            """

    response = model.invoke([
        SystemMessage(content=system_prompt),
        *history,
        HumanMessage(content=prompt)
        ])
    
    return {
        "answer": response.content
        }

def refuse_node(state: AssistantState) -> dict:
    """ Return a response when the documents cannot support an answer."""

    return {
        "answer": ("I don't know based on the provided documents. ")
    }
    
    
    
def route_after_grade(state: AssistantState) -> str:
    """ Decide what the graph should do after grading the documents."""

    if state["supported"]:
        return "answer"

    if state["attempts"] >= 2:
        return "refuse"

    return "retry"