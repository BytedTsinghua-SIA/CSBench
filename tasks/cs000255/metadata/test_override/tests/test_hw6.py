import subprocess
import os
import re
import sys

# Path to the source directory
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HW6_LISP = "hw6.lsp"


def run_lisp(code, timeout=30):
    """
    Runs Lisp code using sbcl and returns the output.
    """
    full_code = f'(progn (load "{HW6_LISP}") {code})'

    command = ["sbcl", "--noinform", "--disable-debugger", "--eval", full_code, "--quit"]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=SRC_DIR,
            timeout=timeout
        )
        if result.returncode != 0:
            print(f"SBCL Error:\n{result.stderr}")
            print(f"SBCL Output:\n{result.stdout}")
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"Timeout after {timeout} seconds")
        return "", "Timeout"


def extract_value(pattern, stdout):
    """
    Extract a numeric value from stdout using regex pattern.
    Returns the integer value, or None if not found.
    """
    match = re.search(pattern, stdout)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def extract_list(pattern, stdout):
    """
    Extract a list of values from stdout using regex pattern.
    Returns the list as a string, or None if not found.
    """
    match = re.search(pattern, stdout)
    if match:
        return match.group(1)
    return None


def test_node2var_basic():
    """Test node2var function with basic inputs."""
    code = """
    (format t "NODE2VAR_1_1_3: ~A~%" (node2var 1 1 3))
    (format t "NODE2VAR_1_2_3: ~A~%" (node2var 1 2 3))
    (format t "NODE2VAR_1_3_3: ~A~%" (node2var 1 3 3))
    (format t "NODE2VAR_2_1_3: ~A~%" (node2var 2 1 3))
    (format t "NODE2VAR_2_2_3: ~A~%" (node2var 2 2 3))
    """
    stdout, stderr = run_lisp(code)

    val = extract_value(r"NODE2VAR_1_1_3: (\d+)", stdout)
    assert val == 1, f"node2var(1,1,3) = {val}, expected 1"

    val = extract_value(r"NODE2VAR_1_2_3: (\d+)", stdout)
    assert val == 2, f"node2var(1,2,3) = {val}, expected 2"

    val = extract_value(r"NODE2VAR_1_3_3: (\d+)", stdout)
    assert val == 3, f"node2var(1,3,3) = {val}, expected 3"

    val = extract_value(r"NODE2VAR_2_1_3: (\d+)", stdout)
    assert val == 4, f"node2var(2,1,3) = {val}, expected 4"

    val = extract_value(r"NODE2VAR_2_2_3: (\d+)", stdout)
    assert val == 5, f"node2var(2,2,3) = {val}, expected 5"

    print("test_node2var_basic passed")


def test_node2var_larger():
    """Test node2var function with larger k values."""
    code = """
    (format t "NODE2VAR_3_5_5: ~A~%" (node2var 3 5 5))
    (format t "NODE2VAR_5_1_10: ~A~%" (node2var 5 1 10))
    """
    stdout, stderr = run_lisp(code)

    val = extract_value(r"NODE2VAR_3_5_5: (\d+)", stdout)
    assert val == 15, f"node2var(3,5,5) = {val}, expected 15"

    val = extract_value(r"NODE2VAR_5_1_10: (\d+)", stdout)
    assert val == 41, f"node2var(5,1,10) = {val}, expected 41"

    print("test_node2var_larger passed")


def test_at_least_one_color_basic():
    """Test at-least-one-color function."""
    code = """
    (format t "AT_LEAST_ONE_1_1_3: ~A~%" (at-least-one-color 1 1 3))
    (format t "AT_LEAST_ONE_1_2_3: ~A~%" (at-least-one-color 1 2 3))
    (format t "AT_LEAST_ONE_1_3_3: ~A~%" (at-least-one-color 1 3 3))
    """
    stdout, stderr = run_lisp(code)

    # at-least-one-color should return a clause: (1 2 3) for colors 1,2,3
    lst = extract_list(r"AT_LEAST_ONE_1_1_3: \((.*?)\)", stdout)
    assert lst is not None, "Could not extract at-least-one-color result"
    assert "1" in lst and "2" in lst and "3" in lst, f"at-least-one-color(1,1,3) should contain 1,2,3, got {lst}"

    # Starting from color 2 should give (2 3)
    lst = extract_list(r"AT_LEAST_ONE_1_2_3: \((.*?)\)", stdout)
    assert lst is not None, "Could not extract at-least-one-color result"
    assert "2" in lst and "3" in lst, f"at-least-one-color(1,2,3) should contain 2,3, got {lst}"

    # Starting from color 3 should give just (3)
    lst = extract_list(r"AT_LEAST_ONE_1_3_3: \((.*?)\)", stdout)
    assert lst is not None, "Could not extract at-least-one-color result"
    assert "3" in lst, f"at-least-one-color(1,3,3) should contain 3, got {lst}"

    print("test_at_least_one_color_basic passed")


def test_at_least_one_color_empty():
    """Test at-least-one-color when c > k."""
    code = """
    (format t "AT_LEAST_ONE_EMPTY: ~A~%" (at-least-one-color 1 4 3))
    """
    stdout, stderr = run_lisp(code)

    # Should return NIL when c > k
    assert "AT_LEAST_ONE_EMPTY: NIL" in stdout or "AT_LEAST_ONE_EMPTY: ()" in stdout, \
        f"at-least-one-color(1,4,3) should return NIL"

    print("test_at_least_one_color_empty passed")


def test_at_most_one_color_basic():
    """Test at-most-one-color function."""
    code = """
    (format t "AT_MOST_ONE_1_1_3: ~A~%" (at-most-one-color 1 1 3))
    """
    stdout, stderr = run_lisp(code)

    # at-most-one-color should return a list of clauses:
    # ((-1 -2) (-1 -3) (-2 -3))
    # This ensures no two colors can both be true
    assert "AT_MOST_ONE_1_1_3:" in stdout, "Could not find at-most-one-color output"

    # Check for negative pairs like (-1 -2), (-1 -3), (-2 -3)
    assert "(-1 -2)" in stdout or "(-1 -3)" in stdout or "(-2 -3)" in stdout, \
        f"at-most-one-color should contain negative pairs, got {stdout}"

    print("test_at_most_one_color_basic passed")


def test_at_most_one_color_count():
    """Test that at-most-one-color generates correct number of clauses."""
    code = """
    (let ((result (at-most-one-color 1 1 3)))
      (format t "AT_MOST_ONE_COUNT: ~A~%" (length result)))
    """
    stdout, stderr = run_lisp(code)

    count = extract_value(r"AT_MOST_ONE_COUNT: (\d+)", stdout)
    # For 3 colors, we need C(3,2) = 3 clauses: (-1 -2), (-1 -3), (-2 -3)
    assert count == 3, f"at-most-one-color(1,1,3) should generate 3 clauses, got {count}"

    print("test_at_most_one_color_count passed")


def test_generate_node_clauses_basic():
    """Test generate-node-clauses function."""
    code = """
    (format t "GEN_NODE_CLAUSES_1_3: ~A~%" (generate-node-clauses 1 3))
    """
    stdout, stderr = run_lisp(code)

    # generate-node-clauses should return:
    # - One clause for "at least one color": (1 2 3)
    # - Plus clauses for "at most one color": ((-1 -2) (-1 -3) (-2 -3))
    # Total: 4 clauses
    assert "GEN_NODE_CLAUSES_1_3:" in stdout, "Could not find generate-node-clauses output"

    # Should contain positive clause (1 2 3) for at-least-one-color
    assert "(1 2 3)" in stdout, f"generate-node-clauses should contain (1 2 3)"

    # Should contain negative pairs for at-most-one-color
    assert "(-1 -2)" in stdout or "(-1 -3)" in stdout or "(-2 -3)" in stdout, \
        f"generate-node-clauses should contain negative pairs"

    print("test_generate_node_clauses_basic passed")


def test_generate_node_clauses_count():
    """Test that generate-node-clauses generates correct number of clauses."""
    code = """
    (let ((result (generate-node-clauses 1 3)))
      (format t "GEN_NODE_COUNT: ~A~%" (length result)))
    """
    stdout, stderr = run_lisp(code)

    count = extract_value(r"GEN_NODE_COUNT: (\d+)", stdout)
    # 1 clause for at-least-one + 3 clauses for at-most-one = 4 clauses
    assert count == 4, f"generate-node-clauses(1,3) should generate 4 clauses, got {count}"

    print("test_generate_node_clauses_count passed")


def test_generate_edge_clauses_basic():
    """Test generate-edge-clauses function."""
    code = """
    (format t "GEN_EDGE_CLAUSES_1_2_3: ~A~%" (generate-edge-clauses '(1 2) 3))
    """
    stdout, stderr = run_lisp(code)

    # generate-edge-clauses should return clauses:
    # ((-1 -4) (-2 -5) (-3 -6))
    # where node 1 has vars 1,2,3 and node 2 has vars 4,5,6
    # For each color c: (-var(node1,c) -var(node2,c))
    assert "GEN_EDGE_CLAUSES_1_2_3:" in stdout, "Could not find generate-edge-clauses output"

    # Should contain negative pairs like (-1 -4), (-2 -5), (-3 -6)
    assert "(-1 -4)" in stdout, f"generate-edge-clauses should contain (-1 -4)"
    assert "(-2 -5)" in stdout, f"generate-edge-clauses should contain (-2 -5)"
    assert "(-3 -6)" in stdout, f"generate-edge-clauses should contain (-3 -6)"

    print("test_generate_edge_clauses_basic passed")


def test_generate_edge_clauses_count():
    """Test that generate-edge-clauses generates correct number of clauses."""
    code = """
    (let ((result (generate-edge-clauses '(1 2) 3)))
      (format t "GEN_EDGE_COUNT: ~A~%" (length result)))
    """
    stdout, stderr = run_lisp(code)

    count = extract_value(r"GEN_EDGE_COUNT: (\d+)", stdout)
    # For 3 colors, we need 3 clauses: one for each color
    assert count == 3, f"generate-edge-clauses((1 2), 3) should generate 3 clauses, got {count}"

    print("test_generate_edge_clauses_count passed")


def test_generate_edge_clauses_larger_k():
    """Test generate-edge-clauses with larger k."""
    code = """
    (let ((result (generate-edge-clauses '(1 2) 5)))
      (format t "GEN_EDGE_COUNT_5: ~A~%" (length result)))
    """
    stdout, stderr = run_lisp(code)

    count = extract_value(r"GEN_EDGE_COUNT_5: (\d+)", stdout)
    # For 5 colors, we need 5 clauses
    assert count == 5, f"generate-edge-clauses((1 2), 5) should generate 5 clauses, got {count}"

    print("test_generate_edge_clauses_larger_k passed")


def test_full_graph_conversion():
    """Test a simple graph coloring conversion."""
    code = """
    ;; Create a simple 2-node graph with 1 edge and 3 colors
    (let* ((edges '((1 2)))
           (node-clauses-1 (generate-node-clauses 1 3))
           (node-clauses-2 (generate-node-clauses 2 3))
           (edge-clauses (generate-edge-clauses '(1 2) 3))
           (all-clauses (append node-clauses-1 node-clauses-2 edge-clauses)))
      (format t "TOTAL_CLAUSES: ~A~%" (length all-clauses)))
    """
    stdout, stderr = run_lisp(code)

    count = extract_value(r"TOTAL_CLAUSES: (\d+)", stdout)
    # 4 clauses for node 1 + 4 clauses for node 2 + 3 edge clauses = 11 clauses
    assert count == 11, f"Total clauses should be 11, got {count}"

    print("test_full_graph_conversion passed")


def test_dual_function():
    """Test the dual (negation) helper function."""
    code = """
    (format t "DUAL_1_2_3: ~A~%" (dual '(1 2 3)))
    """
    stdout, stderr = run_lisp(code)

    assert "(-1 -2 -3)" in stdout or "(-1 -2 -3)" in stdout or "DUAL_1_2_3: (-1 -2 -3)" in stdout, \
        f"dual '(1 2 3) should return (-1 -2 -3), got {stdout}"

    print("test_dual_function passed")


def main():
    """Run all tests."""
    test_functions = [
        test_node2var_basic,
        test_node2var_larger,
        test_at_least_one_color_basic,
        test_at_least_one_color_empty,
        test_at_most_one_color_basic,
        test_at_most_one_color_count,
        test_generate_node_clauses_basic,
        test_generate_node_clauses_count,
        test_generate_edge_clauses_basic,
        test_generate_edge_clauses_count,
        test_generate_edge_clauses_larger_k,
        test_full_graph_conversion,
        test_dual_function,
    ]
    passed = 0
    failed = 0
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"Test {test_func.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"Test {test_func.__name__} error: {e}")
            failed += 1
    print(f"\nTotal tests: {len(test_functions)}, Passed: {passed}, Failed: {failed}")
    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed!")


if __name__ == "__main__":
    main()
