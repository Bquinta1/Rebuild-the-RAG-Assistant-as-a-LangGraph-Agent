from ticket_assistant.graph import build_graph
from ticket_assistant.nodes import route_after_grade


def test_graph_has_expected_nodes_and_edges():
    edges = {(e.source, e.target) for e in build_graph().get_graph().edges}
    assert ("__start__", "retrieve") in edges
    assert ("retrieve", "grade") in edges
    assert ("retry", "retrieve") in edges  # the cycle
    assert ("answer", "__end__") in edges
    assert ("refuse", "__end__") in edges
    for target in {"answer", "retry", "refuse"}:
        assert ("grade", target) in edges
        
def test_cannot_retry_once_attempts_exhausted():
    state = {"supported": False, "attempts": 2}
    assert route_after_grade(state) == "refuse"