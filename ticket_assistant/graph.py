from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage
from .state import AssistantState
from .nodes import retrieve_node, grade_node, retry_node, answer_node, refuse_node, route_after_grade


def build_graph():
    graph = StateGraph(AssistantState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade", grade_node)
    graph.add_node("retry", retry_node)
    graph.add_node("answer", answer_node)
    graph.add_node("refuse", refuse_node)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "grade")

    graph.add_conditional_edges(
        "grade",
        route_after_grade,
        {
            "answer": "answer",
            "retry": "retry",
            "refuse": "refuse",
        },
    )

    graph.add_edge("retry", "retrieve")
    graph.add_edge("answer", END)
    graph.add_edge("refuse", END)
    
    return graph.compile()

def run_repl():
    app = build_graph()
    messages = []

    print("RAG Assistant")
    print("Type 'quit' to exit.")

    while True:
        question = input("\nYou: ").strip()
        if question.lower() == "quit":
            break
        if not question:
            continue
        messages.append(HumanMessage(content=question))
        result = app.invoke(
            {
                "messages": messages,
                "question": question,
                "query": question,
                "documents": [],
                "attempts": 0,
                "supported": False,
                "answer": "",
            }
        )
        answer = result["answer"]
        messages.append(AIMessage(content=answer))
        print(f"\nAssistant: {answer}")

app = build_graph()

if __name__ == "__main__":
    run_repl()