from pathlib import Path
def _assert_paths_exist(paths):
    missing = [str(p) for p in paths if not p.exists()]
    assert not missing, f"Missing required files or directories: {missing}"


def test_project4_core_files_exist():
    cwd = Path(__file__).resolve().parent.parent

    java_root = cwd / "src" / "main" / "java" / "edu" / "berkeley" / "cs186" / "database"
    test_java_root = cwd / "src" / "test" / "java" / "edu" / "berkeley" / "cs186" / "database"

    required_paths = [
        cwd / "pom.xml",
        cwd / "src" / "main" / "resources" / "Courses.csv",
        cwd / "src" / "main" / "resources" / "Enrollments.csv",
        cwd / "src" / "main" / "resources" / "Students.csv",
        java_root / "concurrency" / "LockType.java",
        java_root / "concurrency" / "LockManager.java",
        java_root / "concurrency" / "LockContext.java",
        java_root / "concurrency" / "LockUtil.java",
        java_root / "concurrency" / "ResourceName.java",
        java_root / "concurrency" / "DummyLockManager.java",
        java_root / "memory" / "Page.java",
        java_root / "table" / "PageDirectory.java",
        java_root / "table" / "Table.java",
        java_root / "cli" / "CommandLineInterface.java",
        java_root / "cli" / "Server.java",
        test_java_root / "concurrency" / "TestLockType.java",
        test_java_root / "concurrency" / "TestLockManager.java",
        test_java_root / "concurrency" / "TestLockContext.java",
        test_java_root / "concurrency" / "TestLockUtil.java",
        test_java_root / "TestDatabaseDeadlockPrecheck.java",
        test_java_root / "TestDatabase2PL.java",
    ]

    _assert_paths_exist(required_paths)
