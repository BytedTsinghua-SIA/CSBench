import grader


def test_attack_three():
    try:
        grader.scenario_three()
    except Exception:
        assert False
