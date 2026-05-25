from pathlib import Path


def test_solution_files_exist():
    src_dir = Path(__file__).resolve().parent.parent
    solution_files = [
        "part1_gnn_layers.py",
        "part2_deepsnap_basics.py",
        "part3_deepsnap_advanced.py",
        "part4_link_prediction.py",
    ]
    for file in solution_files:
        assert (src_dir / file).exists(), f"Solution file not found: {file}"