import math
import shutil
import subprocess
from pathlib import Path
from typing import List, Sequence

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent

HARNESS_CODE = r'''
#include <Eigen/Eigen>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

#define main source_main
#include "main.cpp"
#undef main

namespace
{
int pixel_index(int x, int y, int width, int height)
{
    return (height - 1 - y) * width + x;
}
}

int main(int argc, char** argv)
{
    if (argc < 2)
    {
        std::cerr << "Missing harness mode" << std::endl;
        return 1;
    }

    const std::string mode = argv[1];
    std::cout << std::fixed << std::setprecision(6);

    if (mode == "projection")
    {
        const float fov = 45.0f;
        const float aspect = 1.0f;
        const float z_near = 0.1f;
        const float z_far = 50.0f;
        const auto m = get_projection_matrix(fov, aspect, z_near, z_far);
        for (int i = 0; i < 4; ++i)
        {
            for (int j = 0; j < 4; ++j)
            {
                std::cout << m(i, j);
                if (!(i == 3 && j == 3))
                {
                    std::cout << ' ';
                }
            }
        }
        return 0;
    }

    if (mode == "solid")
    {
        constexpr int width = 10;
        constexpr int height = 10;
        rst::rasterizer r(width, height);
        r.clear(rst::Buffers::Color | rst::Buffers::Depth);
        r.set_model(Eigen::Matrix4f::Identity());
        r.set_view(Eigen::Matrix4f::Identity());
        r.set_projection(Eigen::Matrix4f::Identity());

        const std::vector<Eigen::Vector3f> pos{
            {-0.5f, -0.5f, 0.2f},
            {0.5f, -0.5f, 0.2f},
            {-0.2f, 0.6f, 0.2f},
        };
        const std::vector<Eigen::Vector3i> ind{{0, 1, 2}};
        const std::vector<Eigen::Vector3f> col{
            {1.0f, 0.0f, 0.0f},
            {1.0f, 0.0f, 0.0f},
            {1.0f, 0.0f, 0.0f},
        };

        const auto pid = r.load_positions(pos);
        const auto iid = r.load_indices(ind);
        const auto cid = r.load_colors(col);
        r.draw(pid, iid, cid, rst::Primitive::Triangle);

        const auto& buffer = r.frame_buffer();
        int red_pixels = 0;
        for (const auto& c : buffer)
        {
            if (c.x() > 0.1f && c.y() < 1e-4f && c.z() < 1e-4f)
            {
                red_pixels++;
            }
        }

        const int center_index = pixel_index(5, 5, width, height);
        const auto& center = buffer[center_index];
        std::cout << red_pixels << ' ' << center.x() << ' ' << center.y() << ' ' << center.z();
        return 0;
    }

    if (mode == "depth")
    {
        constexpr int width = 4;
        constexpr int height = 4;
        rst::rasterizer r(width, height);
        r.clear(rst::Buffers::Color | rst::Buffers::Depth);
        r.set_model(Eigen::Matrix4f::Identity());
        r.set_view(Eigen::Matrix4f::Identity());
        r.set_projection(Eigen::Matrix4f::Identity());

        const std::vector<Eigen::Vector3f> pos{
            {-0.3f, -0.3f, 0.2f},
            {0.7f, -0.3f, 0.2f},
            {-0.3f, 0.7f, 0.2f},
            {-0.3f, -0.3f, 0.8f},
            {0.7f, -0.3f, 0.8f},
            {-0.3f, 0.7f, 0.8f},
        };
        const std::vector<Eigen::Vector3i> ind{{0, 1, 2}, {3, 4, 5}};
        const std::vector<Eigen::Vector3f> col{
            {1.0f, 0.0f, 0.0f},
            {1.0f, 0.0f, 0.0f},
            {1.0f, 0.0f, 0.0f},
            {0.0f, 0.0f, 1.0f},
            {0.0f, 0.0f, 1.0f},
            {0.0f, 0.0f, 1.0f},
        };

        const auto pid = r.load_positions(pos);
        const auto iid = r.load_indices(ind);
        const auto cid = r.load_colors(col);
        r.draw(pid, iid, cid, rst::Primitive::Triangle);

        const auto& buffer = r.frame_buffer();
        const int center_index = pixel_index(2, 2, width, height);
        const auto& center = buffer[center_index];
        std::cout << center.x() << ' ' << center.y() << ' ' << center.z();
        return 0;
    }

    std::cerr << "Unknown harness mode" << std::endl;
    return 1;
}
'''


def _matrix_multiply(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> List[List[float]]:
    """Compute 4x4 matrix product for projection reference calculations."""
    result: List[List[float]] = [[0.0 for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            for k in range(4):
                result[i][j] += a[i][k] * b[k][j]
    return result


def _projection_reference(fov: float, aspect: float, z_near: float, z_far: float) -> List[List[float]]:
    """Recreate the course projection matrix to validate student implementation."""
    top = math.tan(math.radians(fov) / 2.0) * z_near
    right = top * aspect

    persp = [
        [z_near, 0.0, 0.0, 0.0],
        [0.0, z_near, 0.0, 0.0],
        [0.0, 0.0, z_near + z_far, -z_near * z_far],
        [0.0, 0.0, 1.0, 0.0],
    ]

    ortho_trans = [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, (z_near + z_far) / (z_near - z_far)],
        [0.0, 0.0, 0.0, 1.0],
    ]

    ortho_scale = [
        [1.0 / right, 0.0, 0.0, 0.0],
        [0.0, 1.0 / top, 0.0, 0.0],
        [0.0, 0.0, 2.0 / (z_near - z_far), 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]

    return _matrix_multiply(_matrix_multiply(ortho_scale, ortho_trans), persp)


def _run_pkg_config(pkg: str) -> List[str]:
    """Invoke pkg-config and return split flags if available."""
    try:
        completed = subprocess.run(
            ["pkg-config", "--cflags", "--libs", pkg],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    flags = completed.stdout.strip()
    return flags.split() if flags else []


def _resolve_opencv_flags() -> List[str]:
    """Find usable OpenCV compilation flags via pkg-config."""
    for candidate in ("opencv4", "opencv"):
        flags = _run_pkg_config(candidate)
        if flags:
            return flags
    return []


def _resolve_eigen_includes() -> List[str]:
    """Return include flags for Eigen if common paths exist."""
    includes: List[str] = []
    for path in (Path("/usr/include/eigen3"), Path("/usr/local/include/eigen3")):
        if path.exists():
            includes.extend(["-I", str(path)])
    return includes


def _build_harness(tmp_dir: Path) -> Path:
    """Compile the C++ harness so pytest can exercise rasterizer behavior."""
    gpp = shutil.which("g++")
    if not gpp:
        pytest.skip("缺少 g++，请安装编译器后重试")

    opencv_flags = _resolve_opencv_flags()
    if not opencv_flags:
        pytest.skip("缺少 OpenCV 开发包 (pkg-config 未找到 opencv/opencv4)")

    eigen_flags = _resolve_eigen_includes()

    harness_cpp = tmp_dir / "harness.cpp"
    harness_cpp.write_text(HARNESS_CODE, encoding="utf-8")
    exe_path = tmp_dir / "rasterizer_harness"

    compile_cmd: List[str] = [
        gpp,
        "-std=c++17",
        "-Dmain=source_main",
        str(harness_cpp),
        "rasterizer.cpp",
        "Triangle.cpp",
        "-o",
        str(exe_path),
        "-I",
        str(ROOT_DIR),
        *eigen_flags,
        *opencv_flags,
    ]

    subprocess.run(compile_cmd, cwd=ROOT_DIR, check=True)
    return exe_path


def _run_harness(executable: Path, mode: str) -> List[float]:
    """Execute harness in a given mode and parse whitespace-separated floats."""
    completed = subprocess.run(
        [str(executable), mode],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT_DIR,
    )
    output = completed.stdout.strip()
    if not output:
        return []
    return [float(x) for x in output.split()]


@pytest.fixture(scope="session")
def harness_executable(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scoped build of the harness binary to speed up tests."""
    build_dir = tmp_path_factory.mktemp("harness_build")
    return _build_harness(build_dir)


def test_projection_matrix_matches_reference(harness_executable: Path) -> None:
    """投影矩阵数值必须与课程公式一致，避免返回单位矩阵。"""
    values = _run_harness(harness_executable, "projection")
    assert len(values) == 16, "投影矩阵输出格式异常"

    matrix = [values[i * 4 : (i + 1) * 4] for i in range(4)]
    expected = _projection_reference(45.0, 1.0, 0.1, 50.0)

    for row_out, row_exp in zip(matrix, expected):
        for got, exp in zip(row_out, row_exp):
            assert math.isclose(got, exp, rel_tol=1e-5, abs_tol=1e-5)


def test_triangle_rasterizes_filled_pixels(harness_executable: Path) -> None:
    """三角形应填充一定数量像素，且中心像素应为红色。"""
    results = _run_harness(harness_executable, "solid")
    assert len(results) == 4, "填充测试输出格式异常"

    red_pixels = int(results[0])
    center_r, center_g, center_b = results[1:]

    assert red_pixels >= 5, "三角形未正确栅格化，填充像素过少"
    assert center_r > 0.5 and center_g < 1e-3 and center_b < 1e-3, "中心像素颜色应为红色"


def test_depth_buffer_prefers_near_fragment(harness_executable: Path) -> None:
    """深度缓冲应保留更近的片元，遮挡更远的蓝色三角形。"""
    values = _run_harness(harness_executable, "depth")
    assert len(values) == 3, "深度测试输出格式异常"

    center_r, center_g, center_b = values

    assert center_r > 0.5, "近处红色三角形未覆盖重叠区域"
    assert center_b < 0.2, "远处蓝色三角形错误通过深度测试"
