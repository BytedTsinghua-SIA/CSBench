from pathlib import Path

def test_required_files_exist():
    # Base directory relative to this test file (lab/)
    base_dir = Path(__file__).resolve().parent.parent
    
    # Files to check based on task.txt
    required_files = [
        "lab/raft1/raft_test.go",
        "lab/raft1/raft.go",
        "lab/raft1/server.go",
        "lab/raft1/test.go",
        "lab/raft1/util.go",
        "lab/tester1/annotation.go",
        "lab/tester1/clnts.go",
        "lab/tester1/config.go",
        "lab/tester1/group.go",
        "lab/tester1/persister.go",
        "lab/tester1/srv.go"
    ]
    
    for relative_path in required_files:
        file_path = base_dir / relative_path
        assert file_path.exists(), f"Required file missing: {relative_path}"
