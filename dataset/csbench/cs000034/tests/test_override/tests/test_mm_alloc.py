import ctypes
import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def mm_alloc_dir():
    root = Path(__file__).resolve().parent.parent
    build_dir = root / "mm_alloc"
    subprocess.run(["make", "clean"], cwd=build_dir, check=True)
    subprocess.run(["make"], cwd=build_dir, check=True)
    yield build_dir
    subprocess.run(["make", "clean"], cwd=build_dir, check=True)


@pytest.fixture(scope="session")
def mm_lib(mm_alloc_dir):
    lib_path = mm_alloc_dir / "hw3lib.so"
    lib = ctypes.CDLL(str(lib_path))
    lib.mm_malloc.restype = ctypes.c_void_p
    lib.mm_malloc.argtypes = [ctypes.c_size_t]
    lib.mm_realloc.restype = ctypes.c_void_p
    lib.mm_realloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    lib.mm_free.restype = None
    lib.mm_free.argtypes = [ctypes.c_void_p]
    return lib


def read_bytes(ptr, length):
    return bytearray(ctypes.string_at(ptr, length))


def write_sequence(ptr, length):
    array_type = ctypes.c_uint8 * length
    array = array_type.from_address(ptr)
    for index in range(length):
        array[index] = (index * 7 + 3) & 0xFF


def test_mm_malloc_zeroes_memory(mm_lib):
    length = 64
    ptr = mm_lib.mm_malloc(length)
    assert ptr != 0
    data = read_bytes(ptr, length)
    assert data == bytearray(length)
    mm_lib.mm_free(ptr)


def test_mm_malloc_reuses_and_zeros(mm_lib):
    first = mm_lib.mm_malloc(48)
    assert first != 0
    array_type = ctypes.c_uint8 * 48
    arr = array_type.from_address(first)
    arr[0] = 0xAB
    mm_lib.mm_free(first)

    second = mm_lib.mm_malloc(24)
    assert second == first
    data = read_bytes(second, 24)
    assert data == bytearray(24)
    mm_lib.mm_free(second)


def test_mm_realloc_preserves_content(mm_lib):
    original = mm_lib.mm_malloc(16)
    assert original != 0
    write_sequence(original, 16)
    expected = read_bytes(original, 16)

    expanded = mm_lib.mm_realloc(original, 64)
    assert expanded != 0
    preserved = read_bytes(expanded, 16)
    assert preserved == expected

    mm_lib.mm_free(expanded)


def test_mm_realloc_in_place_growth(mm_lib):
    a = mm_lib.mm_malloc(32)
    b = mm_lib.mm_malloc(32)
    write_sequence(a, 32)
    expected = read_bytes(a, 32)

    mm_lib.mm_free(b)
    grown = mm_lib.mm_realloc(a, 80)
    assert grown == a
    preserved = read_bytes(grown, 32)
    assert preserved == expected
    mm_lib.mm_free(grown)


def test_mm_malloc_zero_size(mm_lib):
    assert mm_lib.mm_malloc(0) in (None, 0)
