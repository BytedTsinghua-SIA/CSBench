from __future__ import annotations

import pytest

from ._julia_harness import run_student_julia


def _fail_with_julia_output(result) -> None:
    msg = "Julia 执行失败\n"
    msg += f"returncode={result.returncode}\n"
    if result.stdout:
        msg += f"--- stdout ---\n{result.stdout}\n"
    if result.stderr:
        msg += f"--- stderr ---\n{result.stderr}\n"
    pytest.fail(msg)


def test_polynomial_core_api() -> None:
    result = run_student_julia(
        r"""
# 1) 结构体字段
@assert :degree in fieldnames(Polynomial)
@assert :coefficients in fieldnames(Polynomial)

# 2) 构造与基本行为
p = Polynomial([1, 2, 3])
@assert getfield(p, :degree) == 2
@assert getfield(p, :coefficients) == [1, 2, 3]

# 3) show 不应抛错
s = sprint(show, p)
@assert length(s) > 0

# 4) 求值（作业注释里给过样例：p(2) == 17）
@assert p(2) == 17

# 5) 导数（作业注释里给过样例）
@assert derivative(Polynomial([1, 2, 3])) == Polynomial([2, 6])
""",
        timeout_seconds=30,
    )
    if result.returncode != 0:
        _fail_with_julia_output(result)


def test_newton_converges() -> None:
    # 允许两种接口：
    # - newton(f, fprime, x0; ...)
    # - newton(f, x0; ...)（若学生自行实现了数值/自动求导）
    result = run_student_julia(
        r"""
# 通用函数：x^2 - 2 = 0
f(x) = x^2 - 2
fp(x) = 2x

x0 = 1.0
seq = nothing
if applicable(newton, f, fp, x0)
    seq = newton(f, fp, x0; tol=1e-10, max_iter=50)
elseif applicable(newton, f, x0)
    seq = newton(f, x0; tol=1e-10, max_iter=50)
else
    error("No supported newton signature found")
end

@assert seq isa AbstractVector
@assert length(seq) >= 2
x = seq[end]
@assert abs(f(x)) < 1e-8

# 多项式专用：x^2 - 2
p = Polynomial([-2, 0, 1])
seqp = newton(p, 1.0; tol=1e-10, max_iter=50)
@assert seqp isa AbstractVector
@assert abs(p(seqp[end])) < 1e-8
""",
        timeout_seconds=30,
    )
    if result.returncode != 0:
        _fail_with_julia_output(result)


def test_cauchy_bounds_and_initial_points() -> None:
    result = run_student_julia(
        r"""
# p(x) = x^2 - 2
p = Polynomial([-2, 0, 1])
L, U = poly_bounds(p)

# 理论值：U=3, L=2/3
@assert abs(U - 3) < 1e-12
@assert abs(L - (2/3)) < 1e-12

zs = initialize_points(p)
@assert zs isa AbstractVector
@assert length(zs) == 2

# 初值应该落在 [L, U]
for z in zs
    @assert L <= abs(z) <= U
end
""",
        timeout_seconds=30,
    )
    if result.returncode != 0:
        _fail_with_julia_output(result)


def test_aberth_finds_roots_degree2() -> None:
    result = run_student_julia(
        r"""
# p(x) = x^2 - 2 的根应为 ±sqrt(2)
p = Polynomial([-2, 0, 1])
out = Aberth(p; tol=1e-10, max_iter=50)

# 兼容两种返回：
# - 直接返回最终点向量
# - 返回每轮迭代的点向量序列（取最后一轮）
final = out
if (out isa AbstractVector) && (length(out) > 0) && (out[1] isa AbstractVector)
    final = out[end]
end

@assert final isa AbstractVector
@assert length(final) == 2

# 将两个根按实部排序后比较
vals = collect(final)
sort!(vals, by=real)

r1, r2 = vals[1], vals[2]
@assert abs(real(r1) + sqrt(2)) < 1e-6 || abs(real(r1) - sqrt(2)) < 1e-6
@assert abs(real(r2) + sqrt(2)) < 1e-6 || abs(real(r2) - sqrt(2)) < 1e-6

# 严格一点：代回多项式，残差应小
for z in vals
    @assert abs(p(z)) < 1e-6
end
""",
        timeout_seconds=60,
    )
    if result.returncode != 0:
        _fail_with_julia_output(result)
