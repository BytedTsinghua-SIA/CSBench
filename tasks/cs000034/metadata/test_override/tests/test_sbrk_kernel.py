from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read(path):
    return (ROOT / path).read_text()


def test_syscall_number_added():
    content = read("pintos/src/lib/syscall-nr.h")
    assert "SYS_SBRK" in content


def test_user_syscall_wrapper():
    content = read("pintos/src/lib/user/syscall.c")
    assert "return (void*)syscall1(SYS_SBRK" in content


def test_kernel_syscall_case():
    content = read("pintos/src/userprog/syscall.c")
    assert "case SYS_SBRK" in content
    assert "syscall_sbrk" in content


def test_thread_struct_has_heap_fields():
    content = read("pintos/src/threads/thread.h")
    assert "heap_base" in content
    assert "brk" in content


def test_process_sets_heap_fields():
    content = read("pintos/src/userprog/process.c")
    assert "t->heap_base" in content
    assert "ROUND_UP" in content
