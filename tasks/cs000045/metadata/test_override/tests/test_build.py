#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试项目是否可以成功使用 CMake 构建。"""

import os
import subprocess
import shutil


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

def run(cmd, cwd=None):
    """运行命令并返回(stdout, stderr)。失败则抛异常。"""
    r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"命令失败: {' '.join(cmd)}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}")
    return r.stdout, r.stderr

def test_cmake_build():
    """构建工程并验证可执行文件存在。"""
    build_dir = os.path.join(ROOT, "build_test")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    # 运行 CMake 生成与构建
    run(["cmake", SRC_DIR], cwd=build_dir)
    run(["cmake", "--build", ".", "-j"], cwd=build_dir)

    exe_path = os.path.join(build_dir, "RayTracing")
    assert os.path.isfile(exe_path), f"未找到可执行文件: {exe_path}"
