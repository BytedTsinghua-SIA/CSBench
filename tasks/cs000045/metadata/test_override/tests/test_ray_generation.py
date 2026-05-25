#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 Render 光线生成是否产生不同像素颜色 (验证每像素方向计算逻辑)。

当前源码中 Render 函数未完成，所有像素方向相同，故该测试将失败，
用于提示需要实现 x,y 及归一化方向。实现后应出现多样颜色。"""

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

def build_and_run():
    build_dir = os.path.join(ROOT, "build_ray")
    if not os.path.isdir(build_dir):
        os.makedirs(build_dir)
        subprocess.check_call(["cmake", SRC_DIR], cwd=build_dir)
        subprocess.check_call(["cmake", "--build", ".", "-j"], cwd=build_dir)
    exe = os.path.join(build_dir, "RayTracing")
    subprocess.check_call([exe], cwd=build_dir)
    ppm = os.path.join(build_dir, "binary.ppm")
    return ppm

def read_ppm_colors(path):
    with open(path, "rb") as f:
        header = f.readline().strip()  # P6
        assert header == b"P6", "PPM 头错误"
        dims = f.readline().strip()
        size_parts = dims.split()
        assert len(size_parts) == 2
        width, height = map(int, size_parts)
        _ = f.readline()  # max value line
        data = f.read()
    # 每 3 字节一个 RGB
    colors = {data[i:i+3] for i in range(0, len(data), 3)}
    return width, height, colors

def test_pixel_color_variance():
    ppm = build_and_run()
    width, height, colors = read_ppm_colors(ppm)
    # 如果所有像素颜色均相同，说明光线生成没有区分像素。
    assert len(colors) > 1, "所有像素颜色相同，需实现每像素独立光线方向生成逻辑。"
    # 合理的最小像素多样性阈值（经验值）：至少 > 10 (场景有球/地面)。
    assert len(colors) > 10, f"颜色种类过少({len(colors)})，可能未正确生成视线方向。"
