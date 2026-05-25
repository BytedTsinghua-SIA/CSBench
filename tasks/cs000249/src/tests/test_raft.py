import subprocess
import sys
from pathlib import Path
import pytest

def run_raft_test(test_name):
    # Base directory where go.mod is located
    base_dir = Path(__file__).resolve().parent.parent / "lab"
    
    # Run go test from the module root
    cmd = f"go test -v -run {test_name} ./raft1"
    
    print(f"\n--- Running Raft Test: {test_name} ---", flush=True)
    
    process = subprocess.Popen(
        cmd,
        cwd=str(base_dir),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    output_lines = []
    for line in process.stdout:
        print(line, end='', flush=True)
        output_lines.append(line)
        
    process.wait()
    
    output = ''.join(output_lines)
    assert process.returncode == 0, f"Test {test_name} failed with exit code {process.returncode}"
    assert "PASS" in output and "FAIL" not in output, (
        f"Test {test_name} failed.\n--- output ---\n{output}\n--------------\n"
    )

# --- Part 3A (Leader Election) ---

def test_initial_election_3a():
    run_raft_test("TestInitialElection3A")

def test_re_election_3a():
    run_raft_test("TestReElection3A")

def test_many_elections_3a():
    run_raft_test("TestManyElections3A")

# --- Part 3B (Log) ---

def test_basic_agree_3b():
    run_raft_test("TestBasicAgree3B")

def test_rpc_bytes_3b():
    run_raft_test("TestRPCBytes3B")

def test_follower_failure_3b():
    run_raft_test("TestFollowerFailure3B")

def test_leader_failure_3b():
    run_raft_test("TestLeaderFailure3B")

def test_fail_agree_3b():
    run_raft_test("TestFailAgree3B")

def test_fail_no_agree_3b():
    run_raft_test("TestFailNoAgree3B")

def test_concurrent_starts_3b():
    run_raft_test("TestConcurrentStarts3B")

def test_rejoin_3b():
    run_raft_test("TestRejoin3B")

def test_backup_3b():
    run_raft_test("TestBackup3B")

def test_count_3b():
    run_raft_test("TestCount3B")

# --- Part 3C (Persistence) ---

def test_persist_1_3c():
    run_raft_test("TestPersist13C")

def test_persist_2_3c():
    run_raft_test("TestPersist23C")

def test_persist_3_3c():
    run_raft_test("TestPersist33C")

def test_figure8_3c():
    run_raft_test("TestFigure83C")

def test_unreliable_agree_3c():
    run_raft_test("TestUnreliableAgree3C")

def test_figure8_unreliable_3c():
    run_raft_test("TestFigure8Unreliable3C")

def test_reliable_churn_3c():
    run_raft_test("TestReliableChurn3C")

def test_unreliable_churn_3c():
    run_raft_test("TestUnreliableChurn3C")

# --- Part 3D (Log Compaction) ---

def test_snapshot_basic_3d():
    run_raft_test("TestSnapshotBasic3D")

def test_snapshot_install_3d():
    run_raft_test("TestSnapshotInstall3D")

def test_snapshot_install_unreliable_3d():
    run_raft_test("TestSnapshotInstallUnreliable3D")

def test_snapshot_install_crash_3d():
    run_raft_test("TestSnapshotInstallCrash3D")

def test_snapshot_install_un_crash_3d():
    run_raft_test("TestSnapshotInstallUnCrash3D")

def test_snapshot_all_crash_3d():
    run_raft_test("TestSnapshotAllCrash3D")

def test_snapshot_init_3d():
    run_raft_test("TestSnapshotInit3D")
