from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, SystemMessage

from .config import BEDROCK_MODEL_ID, AWS_REGION
from .retriever import get_retriever
from .state import AssistantState

def retrieve_node(state: AssistantState) -> dict:
    """Retrieve documents using the current search query."""
    retriever = get_retriever()
    documents = retriever.invoke(state["query"])
    
    return {
        "documents": documents,
        "attempts": state["attempts"] + 1,
    }



def grade_node(state: AssistantState) -> dict:
    if not state["documents"]:
        return {"supported": False}

    context = "\n\n".join(
        f"Source: {document.metadata.get('source', 'unknown')}\n"
        f"{document.page_content}"
        for document in state["documents"]
    )

    model = ChatBedrockConverse(model_id=BEDROCK_MODEL_ID, region_name=AWS_REGION, temperature=0)
    
    prompt = f"""
    You are checking whether retrieved documents contain enough information
    to give the user a useful, accurate answer — even a partial one.

    Question: {state["question"]}
    Retrieved documents: {context}

    If the documents let you answer at least part of the question accurately,
    respond YES. Only respond NO if the documents are unrelated to the
    question or contain no usable information.

    Respond with exactly one word: YES or NO
        """

    response = model.invoke([HumanMessage(content=prompt)])

    supported = response.content.strip().upper() == "YES"
    return {"supported": supported}


def retry_node(state: AssistantState) -> dict:
    """Broaden the query for the second attempt: fixed context terms,
    plus the prior user turn if this looks like a follow-up."""
    prior_user_turns = [
        m.content for m in state["messages"][:-1] if isinstance(m, HumanMessage)
    ]
    context = f" {prior_user_turns[-1]}" if prior_user_turns else ""
    return {
        "query": f'{state["question"]}{context} policy requirements details'
    }


def answer_node(state: AssistantState) -> dict:
    context = "\n\n".join(
        f"Source: {document.metadata.get('source', 'unknown')}\n"
        f"{document.page_content}"
        for document in state["documents"]
    )

    model = ChatBedrockConverse(
        model_id=BEDROCK_MODEL_ID,
        region_name=AWS_REGION,
        temperature=0
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