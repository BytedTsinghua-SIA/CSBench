# GPU 环境下运行
由于本项目的单元测试需要 GPU 支持，请确保在 GPU 环境下运行测试脚本：

```bash
docker run --rm -it --gpus all cs000191 bash -lc "./test.sh"
```

使用原有的 CPU 环境运行测试脚本会报错，如下所示：

```bash
docker run --rm -it cs000191 bash -lc "./test.sh"
```

```
E           RuntimeError: Found no NVIDIA driver on your system. Please check that you have an NVIDIA GPU and installed a driver from http://www.nvidia.com/Download/index.aspx

/usr/local/lib/python3.10/dist-packages/torch/cuda/__init__.py:410: RuntimeError
================================================ short test summary info ================================================
FAILED tests/pytorch101_test.py::TestPyTorch101::test_mm_on_gpu - RuntimeError: Found no NVIDIA driver on your system. Please check that you have an NVIDIA GPU and installed a driver...
```