#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 Sphere::intersect 的命中与未命中及边界情况。"""

import os
import subprocess


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
#include "Sphere.hpp"

int main(){
    Sphere sph(Vector3f(0,0,-5), 1.0f);
    float t; uint32_t idx=0; Vector2f uv;
    bool hit1 = sph.intersect(Vector3f(0,0,0), Vector3f(0,0,-1), t, idx, uv); // 正常命中
    std::cout << "HIT1 " << hit1 << " " << t << "\n";
    bool hit2 = sph.intersect(Vector3f(0,0,0), Vector3f(0,2,-1), t, idx, uv); // 未命中
    std::cout << "HIT2 " << hit2 << "\n";
    bool hit3 = sph.intersect(Vector3f(0,0,-5), Vector3f(0,0,-1), t, idx, uv); // 原点在球面上向内
    std::cout << "HIT3 " << hit3 << " " << t << "\n";
    return 0;
}
"""

def compile_and_run(code: str):
    build_dir = os.path.join(ROOT, "build_sphere")
    if not os.path.isdir(build_dir):
        os.makedirs(build_dir)
    cpp_path = os.path.join(build_dir, "sphere_test.cpp")
    with open(cpp_path, "w", encoding="utf-8") as f:
        f.write(code)
    cmd = ["g++", "-std=c++17", cpp_path, os.path.join(SRC_DIR, "Sphere.hpp"), os.path.join(SRC_DIR, "global.hpp"), os.path.join(SRC_DIR, "Vector.hpp"), "-I"+SRC_DIR, "-o", os.path.join(build_dir, "sphere_test")]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    out = subprocess.check_output([os.path.join(build_dir, "sphere_test")], text=True)
    return out

def test_sphere_intersections():
    out = compile_and_run(TEST_CPP)
    lines = {l.split()[0]: l for l in out.strip().splitlines()}
    # HIT1 正常命中 t>0
    assert lines['HIT1'].split()[1] == '1', "应命中"
    assert float(lines['HIT1'].split()[2]) > 0, "t 应 >0"
    # HIT2 不命中
    assert lines['HIT2'].split()[1] == '0', "不应命中"
    # HIT3: 原点在球内部 (t0 可能为另一根), 逻辑上仍可能命中但 t>0
    hit3_parts = lines['HIT3'].split()
    if hit3_parts[1] == '1':
        assert float(hit3_parts[2]) >= 0, "内部发射 t 应>=0"
    else:
        # 若实现决定返回 false 也接受，但记录警告
        assert False, "从内部射向外部应可命中"
