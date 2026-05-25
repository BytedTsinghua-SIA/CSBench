import pytest
import subprocess
import os
import sys
from pathlib import Path


class TestSimScenes:
    """本地仓库自带 pytest：与评测覆盖版保持一致。"""

    @pytest.fixture(scope="class")
    def test_executable(self):
        test_file = Path(__file__).resolve()
        script_dir = test_file.parent.parent  # src/
        project_root = script_dir.parent  # CS000206/
        current_dir = Path.cwd()

        possible_names = [
            "test_sim_scenes",
            "SimulationTaichi_0_0_1_.._lib_test_sim_scenes",
            "SimulationTaichi_0_0_1_.._lib_test_sim_scenes.exe",
            "test_sim_scenes.exe",
        ]

        possible_paths = []
        for name in possible_names:
            possible_paths += [
                script_dir / "bin" / name,
                project_root / "src" / "bin" / name,
                current_dir / "bin" / name,
                current_dir / "src" / "bin" / name,
                script_dir / "build" / name,
                project_root / "src" / "build" / name,
                current_dir / "build" / name,
            ]

        for path in possible_paths:
            try:
                if path.exists() and os.access(path, os.X_OK):
                    return str(path.resolve())
            except (OSError, PermissionError):
                continue

        if sys.platform != "win32":
            try:
                result = subprocess.run(
                    [
                        "find",
                        str(project_root),
                        "-name",
                        "*test_sim_scenes*",
                        "-type",
                        "f",
                        "-executable",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    found_path = result.stdout.strip().split("\n")[0]
                    if os.path.exists(found_path) and os.access(found_path, os.X_OK):
                        return found_path
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                pass

        raise FileNotFoundError("test_sim_scenes 可执行程序未找到，请确保已编译。")

    def test_snow_E_compare(self, test_executable):
        """测试 Task 1 & 2: 场景构建与 E 的影响"""
        # 对应 C++: snow_E_compare
        result = subprocess.run(
            [test_executable, "snow_E_compare", "--steps", "200"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)

        assert result.returncode == 0, "模拟程序运行失败"
        assert "测试 1" in result.stdout
        assert "结果: 通过" in result.stdout

    def test_water_hit_jelly(self, test_executable):
        """测试 Task 3: 改变物理模型 (场景: 水冲果冻)"""
        # 对应 C++: water_hit_jelly
        result = subprocess.run(
            [test_executable, "water_hit_jelly", "--steps", "200"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)

        assert result.returncode == 0, "模拟程序运行失败"
        assert "测试 2" in result.stdout
        assert "结果: 通过" in result.stdout

    def test_fountain(self, test_executable):
        """测试 Task 3: 改变物理模型 (场景: 喷泉)"""
        # 对应 C++: fountain
        result = subprocess.run(
            [test_executable, "fountain", "--steps", "200"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)

        assert result.returncode == 0, "模拟程序运行失败"
        assert "测试 3" in result.stdout
        assert "结果: 通过" in result.stdout
