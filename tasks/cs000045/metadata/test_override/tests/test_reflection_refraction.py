#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 Renderer.cpp 中的 reflect / refract / fresnel 函数的基本物理性质。"""

import os
import subprocess
import math


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
#include "Vector.hpp"
#include "global.hpp"

// 直接包含实现文件获取函数定义
#include "Renderer.cpp"

int main(){
    // 1. 反射: 入射向量 (0,-1,0), 法线 (0,1,0) => (0,1,0)
    Vector3f I(0,-1,0); Vector3f N(0,1,0);
    Vector3f R = reflect(I,N);
    std::cout << "REFLECT " << R.x << " " << R.y << " " << R.z << "\n";
    // 2. 折射: 空气进入介质 ior=1.5, 入射 (0,-1,0) 法线(0,1,0) => 方向应保持 (0,-1,0)
    Vector3f T = refract(I,N,1.5f);
    std::cout << "REFRACT " << T.x << " " << T.y << " " << T.z << "\n";
    // 3. 菲涅尔: 垂直入射 (0,-1,0) + N(0,1,0)
    float kr = fresnel(I,N,1.5f);
    std::cout << "FRESNEL " << kr << "\n";
    return 0;
}
"""

def compile_and_run(code: str):
    build_dir = os.path.join(ROOT, "build_rrf")
    if not os.path.isdir(build_dir):
        os.makedirs(build_dir)
    cpp_path = os.path.join(build_dir, "rrf_test.cpp")
    with open(cpp_path, "w", encoding="utf-8") as f:
        f.write(code)
    cmd = ["g++", "-std=c++17", cpp_path, "-I"+SRC_DIR, "-o", os.path.join(build_dir, "rrf_test")]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    out = subprocess.check_output([os.path.join(build_dir, "rrf_test")], text=True)
    return out

def test_reflect_refract_fresnel():
    out = compile_and_run(TEST_CPP)
    lines = {l.split()[0]: l for l in out.strip().splitlines()}
    # 反射结果应翻转 y 分量
    r_parts = lines['REFLECT'].split()
    rx, ry, rz = map(float, r_parts[1:])
    assert (abs(rx) < 1e-6 and abs(rz) < 1e-6 and abs(ry-1.0) < 1e-6), "反射方向错误"
    # 折射在法线方向垂直入射时应与入射一致
    t_parts = lines['REFRACT'].split()
    tx, ty, tz = map(float, t_parts[1:])
    assert (abs(tx) < 1e-6 and abs(tz) < 1e-6 and abs(ty + 1.0) < 1e-6), "折射方向应与入射相同 (垂直入射)"
    # 菲涅尔垂直入射反射率应在 (0,1) 之间且较低
    kr = float(lines['FRESNEL'].split()[1])
    assert 0.0 <= kr <= 1.0, "菲涅尔系数范围错误"
    assert kr < 0.2, f"垂直入射反射率不应过高 (kr={kr})"
