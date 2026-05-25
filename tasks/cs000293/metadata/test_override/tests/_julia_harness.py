from __future__ import annotations

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


NOTEBOOK_FILENAME = "problem set 2.ipynb"


@dataclass(frozen=True)
class JuliaRunResult:
    returncode: int
    stdout: str
    stderr: str


def _read_notebook(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def get_notebook_path() -> Path:
    # tests/ -> src/
    return Path(__file__).resolve().parents[1] / NOTEBOOK_FILENAME


def iter_code_cells(nb: dict) -> Iterable[str]:
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", [])
        if isinstance(src, list):
            yield "".join(src)
        elif isinstance(src, str):
            yield src


def select_relevant_cells(code_cells: List[str]) -> List[str]:
    """Pick only the cells needed for algorithmic checks.

    This avoids executing heavyweight / missing packages (e.g., PyPlot).
    """

    required_regexes = [
        r"\bfunction\s+f\s*\(",
        r"\bfunction\s+g\s*\(",
        r"\bstruct\s+Polynomial\b",
        r"\bfunction\s+Polynomial\s*\(",
        r"\bBase\.show\b|\bshow\(io::IO,\s*p::Polynomial\)",
        r"\bfunction\s+\(p::Polynomial\)\(x\)",
        r"\bfunction\s+derivative\s*\(p::Polynomial\)",
        r"\bimport\s+Base:\s*==|\bfunction\s+==\s*\(x::Polynomial,\s*y::Polynomial\)",
        r"\bfunction\s+newton\b",
        r"\bfunction\s+poly_bounds\s*\(p::Polynomial\)",
        r"\bfunction\s+uniform\s*\(a,\s*b\)",
        r"\bfunction\s+calculate_w\s*\(p::Polynomial,\s*pprime::Polynomial,\s*z\)",
        r"\bfunction\s+initialize_points\s*\(p::Polynomial\)",
        r"\bfunction\s+Aberth\s*\(p::Polynomial",
        r"\balpha\s*=\s*2\.5\b",
    ]

    selected: List[str] = []
    for cell in code_cells:
        if "using PyPlot" in cell:
            continue
        if any(re.search(rx, cell) for rx in required_regexes):
            selected.append(cell)

    return selected


def build_student_module_source() -> str:
    nb_path = get_notebook_path()
    nb = _read_notebook(nb_path)
    cells = list(iter_code_cells(nb))
    relevant = select_relevant_cells(cells)

    # Minimal prelude: keep it dependency-free.
    # Student code may rely on Base only.
    prelude = "module StudentSubmission\n"
    postlude = "\nend\n"

    body = "\n\n".join(relevant)
    return prelude + body + postlude


def run_julia(script: str, *, timeout_seconds: int = 30) -> JuliaRunResult:
    """Run a Julia script. Never raises: always returns stdout/stderr/returncode."""
    try:
        completed = subprocess.run(
            [
                "julia",
                "--color=no",
                "--startup-file=no",
                "--history-file=no",
                "-e",
                script,
            ],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        return JuliaRunResult(
            returncode=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
        )
    except FileNotFoundError as e:
        return JuliaRunResult(returncode=127, stdout="", stderr=str(e))
    except subprocess.TimeoutExpired as e:
        return JuliaRunResult(returncode=124, stdout=e.stdout or "", stderr=e.stderr or "")


def run_student_julia(assertions: str, *, timeout_seconds: int = 30) -> JuliaRunResult:
    """Builds a temporary module from the notebook and runs assertions against it."""
    module_src = build_student_module_source()

    # Put everything into a single -e payload to avoid filesystem assumptions.
    # We keep it self-contained and print context on failure.
    payload = (
        module_src
        + "\n"
        + "using .StudentSubmission\n"
        + "try\n"
        + assertions
        + "\nprintln(\"__PYTEST_OK__\")\n"
        + "catch err\n"
        + "println(\"__PYTEST_FAIL__\")\n"
        + "showerror(stdout, err)\n"
        + "println()\n"
        + "Base.show_backtrace(stdout, catch_backtrace())\n"
        + "exit(1)\n"
        + "end\n"
    )

    return run_julia(payload, timeout_seconds=timeout_seconds)
