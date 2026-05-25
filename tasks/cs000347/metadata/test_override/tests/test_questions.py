import grader


def test_questions_file():
    try:
        grader.test_questions()
    except Exception:
        assert False
