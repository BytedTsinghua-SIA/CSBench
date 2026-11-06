from tests.utils import run_node


def test_initial_state():
    result = run_node("unicafe/reducer.js", "counterReducer", [None, {"type": "INIT"}])
    assert result["ok"]
    assert result["result"] == {"good": 0, "ok": 0, "bad": 0}


def test_good_ok_bad_and_reset():
    state = {"good": 0, "ok": 0, "bad": 0}
    good = run_node("unicafe/reducer.js", "counterReducer", [state, {"type": "GOOD"}])
    ok = run_node("unicafe/reducer.js", "counterReducer", [good["result"], {"type": "OK"}])
    bad = run_node("unicafe/reducer.js", "counterReducer", [ok["result"], {"type": "BAD"}])
    reset = run_node("unicafe/reducer.js", "counterReducer", [bad["result"], {"type": "RESET"}])
    assert reset["ok"]
    assert reset["result"] == {"good": 0, "ok": 0, "bad": 0}


def test_apply_feedback_sequence():
    actions = [{"type": "GOOD"}, {"type": "GOOD"}, {"type": "BAD"}]
    result = run_node("unicafe/reducer.js", "applyFeedbackSequence", [actions])
    assert result["ok"]
    assert result["result"] == {"good": 2, "ok": 0, "bad": 1}
