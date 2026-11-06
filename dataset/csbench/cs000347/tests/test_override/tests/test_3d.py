import grader


def test_problem_3d():
    try:
        grader.test_3d()
    except Exception:
        assert False
