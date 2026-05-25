"""
Pytest tests for CS188 Pacman Search Project

These tests wrap the original autograder tests using subprocess.
"""
import subprocess
import os
import sys

# Path to autograder.py
AUTograder_PATH = os.path.join(os.path.dirname(__file__), '..', 'autograder.py')


def run_autograder_question(question):
    """Run autograder for a specific question and return the result."""
    result = subprocess.run(
        [sys.executable, AUTograder_PATH, '-q', question],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(AUTograder_PATH)
    )

    output = result.stdout + result.stderr

    # Check if the question passed by looking for the grade
    # Extract score from output like "### Question q1: 3/3 ###"
    for line in output.split('\n'):
        if f'Question {question}:' in line:
            # Parse score
            parts = line.split(':')
            if len(parts) >= 2:
                score_part = parts[1].strip()
                if '/' in score_part:
                    numerator = int(score_part.split('/')[0])
                    denominator = int(score_part.split('/')[1].split()[0])
                    return numerator == denominator, output, (numerator, denominator)

    return False, output, (0, 0)


def get_expanded_nodes(output):
    """Extract number of expanded nodes from autograder output."""
    for line in output.split('\n'):
        if 'expanded nodes:' in line or 'nodes expanded:' in line:
            try:
                # Extract number from line like "expanded nodes: 1136"
                parts = line.split(':')
                if len(parts) >= 2:
                    return int(parts[1].strip())
            except:
                pass
    return None


class TestQuestion1DFS:
    """Test Q1: Depth First Search"""

    def test_q1_passes(self):
        """Test that DFS implementation passes all tests"""
        passed, output, score = run_autograder_question('q1')
        assert passed, f"Q1 failed with score {score[0]}/{score[1]}\nOutput:\n{output}"


class TestQuestion2BFS:
    """Test Q2: Breadth First Search"""

    def test_q2_passes(self):
        """Test that BFS implementation passes all tests"""
        passed, output, score = run_autograder_question('q2')
        assert passed, f"Q2 failed with score {score[0]}/{score[1]}\nOutput:\n{output}"


class TestQuestion3UCS:
    """Test Q3: Uniform Cost Search"""

    def test_q3_passes(self):
        """Test that UCS implementation passes all tests"""
        passed, output, score = run_autograder_question('q3')
        assert passed, f"Q3 failed with score {score[0]}/{score[1]}\nOutput:\n{output}"


class TestQuestion4AStar:
    """Test Q4: A* Search"""

    def test_q4_passes(self):
        """Test that A* implementation passes all tests"""
        passed, output, score = run_autograder_question('q4')
        assert passed, f"Q4 failed with score {score[0]}/{score[1]}\nOutput:\n{output}"


class TestQuestion5CornersProblem:
    """Test Q5: Corners Problem"""

    def test_q5_passes(self):
        """Test that CornersProblem implementation passes all tests"""
        passed, output, score = run_autograder_question('q5')
        assert passed, f"Q5 failed with score {score[0]}/{score[1]}\nOutput:\n{output}"


class TestQuestion6CornersHeuristic:
    """Test Q6: Corners Heuristic"""

    def test_q6_passes(self):
        """Test that cornersHeuristic passes all tests"""
        passed, output, score = run_autograder_question('q6')
        assert passed, f"Q6 failed with score {score[0]}/{score[1]}\nOutput:\n{output}"

    def test_q6_node_expansion(self):
        """Test that cornersHeuristic expands reasonable number of nodes"""
        passed, output, score = run_autograder_question('q6')
        assert passed, f"Q6 failed with score {score[0]}/{score[1]}"
        # Should expand less than 2000 nodes for full credit
        nodes = get_expanded_nodes(output)
        if nodes is not None:
            assert nodes <= 2000, f"Q6 expanded {nodes} nodes, expected <= 2000"


class TestQuestion7FoodHeuristic:
    """Test Q7: Food Heuristic"""

    def test_q7_passes(self):
        """Test that foodHeuristic passes all tests"""
        passed, output, score = run_autograder_question('q7')
        assert passed, f"Q7 failed with score {score[0]}/{score[1]}\nOutput:\n{output}"


class TestQuestion8ClosestDot:
    """Test Q8: Closest Dot Search"""

    def test_q8_passes(self):
        """Test that ClosestDotSearchAgent passes all tests"""
        passed, output, score = run_autograder_question('q8')
        assert passed, f"Q8 failed with score {score[0]}/{score[1]}\nOutput:\n{output}"


class TestAllQuestions:
    """Test all questions together"""

    def test_all_questions_pass(self):
        """Test that all questions pass"""
        questions = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8']
        total_score = 0
        total_possible = 0
        failed = []

        for q in questions:
            passed, output, score = run_autograder_question(q)
            total_score += score[0]
            total_possible += score[1]
            if not passed:
                failed.append(f"{q}: {score[0]}/{score[1]}")

        # All questions should pass with full score
        assert total_score == total_possible, \
            f"Total score: {total_score}/{total_possible}. Failed: {failed}"
