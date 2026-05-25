from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


NOTEBOOK_FILENAME = "problem set 2.ipynb"


def _notebook_path() -> Path:
    return Path(__file__).resolve().parents[1] / NOTEBOOK_FILENAME


def _load_notebook() -> dict:
    path = _notebook_path()
    return json.loads(path.read_text(encoding="utf-8"))


def _all_code_text(nb: dict) -> str:
    chunks: list[str] = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", [])
        if isinstance(src, list):
            chunks.append("".join(src))
        elif isinstance(src, str):
            chunks.append(src)
    return "\n\n".join(chunks)


@pytest.mark.parametrize(
    "pattern, desc",
    [
        (r"\bfunction\s+f\s*\(", "Exercise1: f(alpha, x)"),
        (r"\bfunction\s+g\s*\(", "Exercise1: g(x)"),
        (r"\bstruct\s+Polynomial\b", "Exercise2: struct Polynomial"),
        (r"\bfunction\s+Polynomial\s*\(", "Exercise2: Polynomial constructor"),
        (r"\bfunction\s+\(p::Polynomial\)\(x\)", "Exercise2: polynomial call overload"),
        (r"\bfunction\s+derivative\s*\(p::Polynomial\)", "Exercise2: derivative"),
        (r"\bfunction\s+==\s*\(x::Polynomial,\s*y::Polynomial\)", "Exercise2: =="),
        (r"\bfunction\s+newton\b", "Exercise3: newton"),
        (r"\bfunction\s+poly_bounds\s*\(p::Polynomial\)", "Exercise4: poly_bounds"),
        (r"\bfunction\s+uniform\s*\(a,\s*b\)", "Exercise4: uniform"),
        (r"\bfunction\s+calculate_w\s*\(", "Exercise4: calculate_w"),
        (r"\bfunction\s+initialize_points\s*\(p::Polynomial\)", "Exercise4: initialize_points"),
        (r"\bfunction\s+Aberth\s*\(p::Polynomial", "Exercise4: Aberth"),
    ],
)
def test_required_definitions_exist(pattern: str, desc: str) -> None:
    nb = _load_notebook()
    code = _all_code_text(nb)
    assert re.search(pattern, code), f"缺少定义：{desc}（未匹配到 {pattern}）"


def test_no_global_not_implemented_placeholders() -> None:
    """保证核心实现不再是占位符。

    这里做的是“强约束”：如果还存在 error(\"Not implemented\")，就直接 fail。
    这样 UT 只会 fail/pass，不会在运行时因调用占位符而 error。
    """

    nb = _load_notebook()
    code = _all_code_text(nb)

    # 允许 markdown 里提到 Not implemented，但 code 里不允许。
    assert "error(\"Not implemented\")" not in code, "仍存在 error(\"Not implemented\") 占位实现"

    # TODO 可保留在非核心区域；但本作业核心函数实现不应保留 TODO 标记。
    # 若你希望更宽松，可删掉这条断言。
    forbidden_todo_targets = [
        "function f(alpha, x)",
        "function g(x)",
        "struct Polynomial",
        "function Polynomial(coeffs::AbstractVector)",
        "function (p::Polynomial)(x)",
        "function derivative(p::Polynomial)",
        "function ==(x::Polynomial, y::Polynomial)",
        "function newton(",
        "function poly_bounds(p::Polynomial)",
        "function uniform(a, b)",
        "function calculate_w(p::Polynomial, pprime::Polynomial, z)",
        "function initialize_points(p::Polynomial)",
        "function Aberth(p::Polynomial",
    ]

    for anchor in forbidden_todo_targets:
        # 若 anchor 附近仍含 TODO，则 fail。
        idx = code.find(anchor)
        if idx == -1:
            continue
        window = code[idx : idx + 400]
        assert "TODO" not in window, f"{anchor} 附近仍包含 TODO 占位"
