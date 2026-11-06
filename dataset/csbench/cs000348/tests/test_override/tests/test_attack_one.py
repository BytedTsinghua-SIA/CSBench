import grader


def test_attack_one():
    try:
        grader.scenario_one()
    except Exception:
        assert False
