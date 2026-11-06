#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 Möller–Trumbore 三角形相交函数 rayTriangleIntersect。

当前源码未实现 (返回 false)，故所有正例测试会失败，
用于驱动实现。"""

import os
import subprocess
import tempfile


def find_repo_root(start: str) -> str:
    """向上查找包含 CMakeLists.txt 的目录（或包含 src/CMakeLists.txt 的仓库根）。"""
    cur = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(cur, "CMakeLists.txt")):
            return cur
        src_cmake = os.path.join(cur, "src", "CMakeLists.txt")
        if os.path.isfile(src_cmake):
            return os.path.join(cur, "src")
        parent = os.path.dirname(cur)
        if parent == cur:
            raise RuntimeError("未找到项目的 CMakeLists.txt")
        cur = parent


ROOT = find_repo_root(os.path.dirname(__file__))
SRC_DIR = ROOT

TEST_CPP = r"""
#include <iostream>
#include <cmath>
#include "Triangle.hpp"

int main(){
    Vector3f v0(0,0,-5); // 简单在 z=-5 的三角形
    Vector3f v1(1,0,-5);
    Vector3f v2(0,1,-5);
    // 1. 正向命中: 射线原点(0,0,0), 方向(0,0,-1)
    float t,u,v; bool hit = rayTriangleIntersect(v0,v1,v2, Vector3f(0,0,0), Vector3f(0,0,-1), t,u,v);
    std::cout << "CASE1 " << hit << " " << t << " " << u << " " << v << "\n";
    // 2. 平行: 方向与平面平行
    hit = rayTriangleIntersect(v0,v1,v2, Vector3f(0,0,0), Vector3f(1,0,0), t,u,v);
    std::cout << "CASE2 " << hit << "\n";
    // 3. 命中在三角形外: 指向 (2,2,-5)
    hit = rayTriangleIntersect(v0,v1,v2, Vector3f(0,0,0), Vector3f(2,2,-5), t,u,v);
    std::cout << "CASE3 " << hit << "\n";
    // 4. 交点在原点后方 (t<0): 原点移动到三角形后面
    hit = rayTriangleIntersect(v0,v1,v2, Vector3f(0,0,-10), Vector3f(0,0,1), t,u,v);
    std::cout << "CASE4 " << hit << "\n";
    return 0;
}
"""

def compile_and_run(src_code: str):
    build_dir = os.path.join(ROOT, "build_tri")
    if not os.path.isdir(build_dir):
        os.makedirs(build_dir)
    cpp_path = os.path.join(build_dir, "tri_test.cpp")
    with open(cpp_path, "w", encoding="utf-8") as f:
        f.write(src_code)
    # 编译: 仅需要 Triangle.hpp, Object.hpp, Vector.hpp, global.hpp
    cmd = ["g++", "-std=c++17", cpp_path, os.path.join(SRC_DIR, "Triangle.hpp"), "-I"+SRC_DIR, "-o", os.path.join(build_dir, "tri_test")]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"编译失败:\n{r.stderr}")
    exe = os.path.join(build_dir, "tri_test")
    out = subprocess.check_output([exe], text=True)
    return out

def test_triangle_intersections():
    out = compile_and_run(TEST_CPP)
    lines = {l.split()[0]: l for l in out.strip().splitlines()}
    # CASE1 期望命中, t>0, u,v >=0 且 u+v<=1
    if "CASE1" in lines:
        parts = lines["CASE1"].split()
        hit = parts[1] == '1'
        if hit:
            t = float(parts[2]); u = float(parts[3]); v = float(parts[4])
            assert t > 0, "t 应该 >0"
            assert u >= 0 and v >= 0 and u+v <= 1, "重心坐标不合法"
        else:
            # 未命中 => 当前实现缺失, 明确失败
            assert False, "rayTriangleIntersect 未实现导致命中失败"
    # CASE2 应该不命中
    assert lines["CASE2"].split()[1] == '0', "平行射线不应命中"
    # CASE3 应该不命中
    assert lines["CASE3"].split()[1] == '0', "射线指向三角形外部不应命中"
    # CASE4 应该不命中 (交点在原点后)
    assert lines["CASE4"].split()[1] == '0', "t<0 的交点不应被视为命中"
