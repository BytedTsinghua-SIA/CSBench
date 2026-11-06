"""
Pytest tests for CS000258 Logic Planning Project.
These tests invoke the original autograder and check the results.
"""

import subprocess
import sys
import os
import re

# Test configuration
TIMEOUT = 600  # 10 minutes


def run_autograder_question(question):
    """Run autograder for a specific question and return the output."""
    # Get the src directory (parent of tests/)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(test_dir)
    autograder_path = os.path.join(src_dir, "autograder.py")

    result = subprocess.run(
        [sys.executable, autograder_path, "-q", question, "--no-graphics"],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        cwd=src_dir
    )
    return result.stdout + result.stderr, result.returncode


def extract_grade(output, question):
    """
    Extract the grade for a question from autograder output.

    Uses multiple regex patterns to handle different output formats:
    - "### Question q1: 2/2 ###"
    - "Question q1: 2/2"
    - "Question q1: 2/2" (in Provisional grades section)

    Returns the highest score found among all matches to handle cases where
    multiple score lines might appear in the output.
    """
    all_scores = []

    # Pattern 1: Look for "### Question qX: N/M ###" format
    pattern1 = rf'###\s*Question\s+{re.escape(question)}\s*:\s*(\d+)\s*/\s*(\d+)\s*###'
    for match in re.finditer(pattern1, output):
        all_scores.append((int(match.group(1)), int(match.group(2))))

    # Pattern 2: Look for "Question qX: N/M" format (e.g., in Provisional grades section)
    pattern2 = rf'Question\s+{re.escape(question)}\s*:\s*(\d+)\s*/\s*(\d+)'
    for match in re.finditer(pattern2, output):
        all_scores.append((int(match.group(1)), int(match.group(2))))

    # If we found scores, return the one with highest numerator (best score)
    if all_scores:
        # Sort by numerator (descending) and return the highest
        best_score = max(all_scores, key=lambda x: x[0])
        return best_score

    # Pattern 3: Check for total score line "Total: N/M" (fallback)
    # This is useful when only one question is tested
    total_pattern = r'Total\s*:\s*(\d+)\s*/\s*(\d+)'
    total_match = re.search(total_pattern, output)
    if total_match:
        # Verify this is a single-question run by checking there's only one question output
        total_numerator = int(total_match.group(1))
        total_denominator = int(total_match.group(2))
        # Check if the question header appears in output
        if f'Question {question}' in output:
            return total_numerator, total_denominator

    # Pattern 4: Count PASS/FAIL patterns as last resort
    # Look for "*** PASS:" or "*** FAIL:" patterns
    pass_pattern = rf'\*\*\*\s*PASS:\s*test_cases/{re.escape(question)}/'
    fail_pattern = rf'\*\*\*\s*FAIL:\s*test_cases/{re.escape(question)}/'
    pass_count = len(re.findall(pass_pattern, output))
    fail_count = len(re.findall(fail_pattern, output))

    if pass_count > 0 or fail_count > 0:
        # Return score as pass_count out of total attempts
        total_attempts = pass_count + fail_count
        return pass_count, total_attempts

    return None, None


class TestQuestion1:
    """Tests for Question 1 - Logic Expressions"""

    def test_q1_logic_expressions(self):
        """Test that question 1 logic expression functions work correctly."""
        output, _ = run_autograder_question("q1")
        numerator, denominator = extract_grade(output, "q1")
        assert numerator is not None, "Could not find grade for q1"
        # Must get full score to pass
        assert numerator == denominator, f"Question 1 must get full score: {numerator}/{denominator}"


class TestQuestion2:
    """Tests for Question 2 - CNF Logic Helper Functions"""

    def test_q2_cnf_helpers(self):
        """Test that question 2 CNF helper functions work correctly."""
        output, _ = run_autograder_question("q2")
        numerator, denominator = extract_grade(output, "q2")
        assert numerator is not None, "Could not find grade for q2"
        assert numerator == denominator, f"Question 2 not passing: {numerator}/{denominator}"


class TestQuestion3:
    """Tests for Question 3 - Pacman Successor Axioms"""

    def test_q3_successor_axioms(self):
        """Test that question 3 successor axiom functions work correctly."""
        output, _ = run_autograder_question("q3")
        numerator, denominator = extract_grade(output, "q3")
        assert numerator is not None, "Could not find grade for q3"
        # Must get full score to pass
        assert numerator == denominator, f"Question 3 must get full score: {numerator}/{denominator}"


class TestQuestion4:
    """Tests for Question 4 - Position Logic Planning"""

    def test_q4_position_planning(self):
        """Test that question 4 position planning function works."""
        output, _ = run_autograder_question("q4")
        numerator, denominator = extract_grade(output, "q4")
        assert numerator is not None, "Could not find grade for q4"
        # Must get full score to pass
        assert numerator == denominator, f"Question 4 must get full score: {numerator}/{denominator}"


class TestQuestion5:
    """Tests for Question 5 - Food Logic Planning"""

    def test_q5_food_planning(self):
        """Test that question 5 food planning function works."""
        output, _ = run_autograder_question("q5")
        numerator, denominator = extract_grade(output, "q5")
        assert numerator is not None, "Could not find grade for q5"
        # Must get full score to pass
        assert numerator == denominator, f"Question 5 must get full score: {numerator}/{denominator}"


class TestQuestion6:
    """Tests for Question 6 - Localization"""

    def test_q6_localization(self):
        """Test that question 6 localization function works."""
        output, _ = run_autograder_question("q6")
        numerator, denominator = extract_grade(output, "q6")
        assert numerator is not None, "Could not find grade for q6"
        # Must get full score to pass
        assert numerator == denominator, f"Question 6 must get full score: {numerator}/{denominator}"


class TestQuestion7:
    """Tests for Question 7 - Mapping"""

    def test_q7_mapping(self):
        """Test that question 7 mapping function works."""
        output, _ = run_autograder_question("q7")
        numerator, denominator = extract_grade(output, "q7")
        assert numerator is not None, "Could not find grade for q7"
        # Must get full score to pass
        assert numerator == denominator, f"Question 7 must get full score: {numerator}/{denominator}"


class TestQuestion8:
    """Tests for Question 8 - SLAM"""

    def test_q8_slam(self):
        """Test that question 8 SLAM function works."""
        output, _ = run_autograder_question("q8")
        numerator, denominator = extract_grade(output, "q8")
        assert numerator is not None, "Could not find grade for q8"
        # Must get full score to pass
        assert numerator == denominator, f"Question 8 must get full score: {numerator}/{denominator}"

