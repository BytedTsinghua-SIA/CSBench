from pathlib import Path
import pytest

def test_framework_files_exist():
    # Determine the project root directory (CS000337_before/src)
    # This file is at CS000337_before/src/tests/test_framework.py
    cwd = Path(__file__).resolve().parent.parent
    
    files_to_check = [
        # Config
        "Cargo.toml",
        
        # Source Files
        "lab/lib.rs",
        "lab/bin/hello_server.rs",
        "lab/hello_server/cache.rs",
        "lab/hello_server/tcp.rs",
        "lab/hello_server/thread_pool.rs",
        "lab/linked_list.rs",
        "lab/list_set/fine_grained.rs",
        "lab/list_set/optimistic_fine_grained.rs",
        "lab/arc.rs",
        "lab/hazard_pointer/hazard.rs",
        "lab/hazard_pointer/retire.rs",
        "lab/hash_table/growable_array.rs",
        "lab/hash_table/split_ordered_list.rs",
        "lab/boc.rs",
        
        # Test Files
        "tests/cache.rs",
        "tests/tcp.rs",
        "tests/thread_pool.rs",
        "tests/linked_list.rs",
        "tests/list_set/main.rs",
        "tests/list_set/fine_grained.rs",
        "tests/list_set/optimistic_fine_grained.rs",
        "tests/arc.rs",
        "tests/hazard_pointer.rs",
        "tests/growable_array.rs",
        "tests/split_ordered_list.rs",
        "tests/boc.rs",
    ]
    
    missing_files = []
    for file_path in files_to_check:
        path = cwd / file_path
        if not path.exists():
            missing_files.append(file_path)
            
    assert not missing_files, f"Missing framework files: {missing_files}"
