from ticket_assistant.nodes import route_after_grade

def test_supported_routes_to_answer():
    assert route_after_grade({"supported": True, "attempts": 1}) == "answer"

def test_unsupported_with_attempts_left_routes_to_retry():
    assert route_after_grade({"supported": False, "attempts": 1}) == "retry"

def test_unsupported_out_of_attempts_routes_to_refuse():
    assert route_after_grade({"supported": False, "attempts": 2}) == "refuse"
    
def test_cannot_retry_once_attempts_exhausted():
    state = {"supported": False, "attempts": 2}
    assert route_after_grade(state) == "refuse"