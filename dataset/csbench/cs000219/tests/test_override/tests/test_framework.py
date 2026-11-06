from pathlib import Path


def _assert_paths_exist(paths):
    missing = [str(p) for p in paths if not p.exists()]
    assert not missing, f"Missing required files or directories: {missing}"


def test_project3_core_files_exist():
    cwd = Path(__file__).resolve().parent.parent

    java_root = cwd / "src" / "main" / "java" / "edu" / "berkeley" / "cs186" / "database"
    test_java_root = cwd / "src" / "test" / "java" / "edu" / "berkeley" / "cs186" / "database"

    required_paths = [
        cwd / "pom.xml",
        cwd / "src" / "main" / "resources" / "Courses.csv",
        cwd / "src" / "main" / "resources" / "Enrollments.csv",
        cwd / "src" / "main" / "resources" / "Students.csv",
        java_root / "common" / "iterator" / "BacktrackingIterator.java",
        java_root / "common" / "iterator" / "ArrayBacktrackingIterator.java",
        java_root / "query" / "QueryOperator.java",
        java_root / "query" / "JoinOperator.java",
        java_root / "query" / "QueryPlan.java",
        java_root / "query" / "SortOperator.java",
        java_root / "query" / "disk" / "Partition.java",
        java_root / "query" / "disk" / "Run.java",
        java_root / "query" / "join" / "BNLJOperator.java",
        java_root / "query" / "join" / "PNLJOperator.java",
        java_root / "query" / "join" / "GHJOperator.java",
        java_root / "query" / "join" / "SHJOperator.java",
        java_root / "query" / "join" / "SortMergeOperator.java",
        test_java_root / "query" / "TestNestedLoopJoin.java",
        test_java_root / "query" / "TestGraceHashJoin.java",
        test_java_root / "query" / "TestSortOperator.java",
        test_java_root / "query" / "TestSortMergeJoin.java",
        test_java_root / "query" / "TestSingleAccess.java",
        test_java_root / "query" / "TestOptimizationJoins.java",
    ]

    _assert_paths_exist(required_paths)
