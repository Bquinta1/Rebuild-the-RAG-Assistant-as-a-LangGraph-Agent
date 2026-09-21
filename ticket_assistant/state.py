""" State that will be used by every node in our graph """


from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langchain_core.documents import Document
from operator import add

class AssistantState(TypedDict):

    messages: Annotated[list[AnyMessage], add_messages]
     
    question: str
    
    query: str
    
    documents: Annotated[list[Document], add]
    
    attempts: int
    
    supported: bool
    
    answer: str