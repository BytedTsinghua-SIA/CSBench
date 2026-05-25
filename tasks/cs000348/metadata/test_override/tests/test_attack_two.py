import grader


def test_attack_two():
    try:
        grader.scenario_two()
    except Exception:
        assert False
