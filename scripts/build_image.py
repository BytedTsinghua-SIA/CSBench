#!/usr/bin/env python3
"""
Generic build script for course tasks.

Usage:
  python3 scripts/build_image.py <assignment_dir> [--image IMAGE] [--tag TAG]
                         [--dockerfile PATH] [--platform PLATFORM]
                         [--push]

- Creates/cleans a staged build directory under BUILD_ROOT/<task_name>.
- Copies all files from the assignment task source into BUILD_ROOT/<task_name>.
- Copies the Dockerfile from 'metadata/Dockerfile' (or --dockerfile) into the staged build directory.
- Runs `docker build` using the build directory as context, targeting amd64 by default.
- Keeps the image local by default unless `--push` is specified.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Sequence

from src.config import (
    BUILD_ROOT,
    DOCKER_NAMESPACE,
    DOCKER_REGISTRY,
    DOCKER_TAG,
    get_default_image_name,
    get_task_build_dir,
    get_task_dir,
)
import urllib.request


EXCLUDE_NAMES = {"metadata", ".git", ".DS_Store"}


# 添加国家检测逻辑，用于自动配置 pip 镜像源
def detect_country() -> Optional[str]:
    """
    检测当前所在国家/地区，用于决定是否使用国内镜像源。
    尝试多个 API 端点，返回国家代码（如 'CN'）或 None。
    """
    urls = [
        "https://ipapi.co/country/",
        "https://ipinfo.io/country",
        "https://ifconfig.co/country-iso",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as resp:
                country = resp.read().decode("utf-8").strip().upper()
                if country:
                    return country
        except Exception:
            continue
    return None


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage build context, run docker build, optionally push image",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "assignment_dir",
        help="Path to the assignment directory (e.g., cmu-cs-ics-attack-lab-phase1)",
    )
    parser.add_argument(
        "--image",
        default=None,
        help="Full Docker image name (overrides registry/namespace defaults)",
    )
    parser.add_argument(
        "--registry",
        default=DOCKER_REGISTRY,
        help="Docker registry hostname",
    )
    parser.add_argument(
        "--namespace",
        default=DOCKER_NAMESPACE,
        help="Registry namespace (project) name",
    )
    parser.add_argument(
        "--tag",
        default=DOCKER_TAG,
        help="Docker image tag",
    )
    parser.add_argument(
        "--dockerfile",
        default=None,
        help="Path to Dockerfile to use (defaults to <assignment_dir>/metadata/Dockerfile)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force rebuild even if image exists",
    )
    parser.add_argument(
        "--no-lock",
        action="store_false",
        dest="lock",
        help="Lock the image build process, prevent concurrent builds",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push the image to remote registry after a successful build",
    )
    parser.add_argument(
        "--use-pip-mirror",
        action="store_true",
        help="Use CN pip mirror if country is detected as CN, speed up pip install",
    )
    return parser.parse_args(argv)


def remove_dir_if_exists(path: Path) -> None:
    if path.exists():
        if path.is_symlink() or path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)


def copy_tree(src_dir: Path, dst_dir: Path, exclude_names: set[str]) -> None:
    for entry in src_dir.iterdir():
        name = entry.name
        # Avoid copying the destination/build directory into itself and excluded names
        if name in exclude_names or entry.samefile(dst_dir) if dst_dir.exists() else False:
            continue
        src_path = entry
        dst_path = dst_dir / name
        if entry.is_symlink():
            # Resolve symlink content by copying the file tree it points to when possible
            resolved = entry.resolve()
            if resolved.is_file():
                shutil.copy2(resolved, dst_path)
            elif resolved.is_dir():
                shutil.copytree(resolved, dst_path, dirs_exist_ok=True)
            else:
                # Skip broken links
                continue
        elif entry.is_file():
            shutil.copy2(src_path, dst_path)
        elif entry.is_dir():
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)


#  添加 use_cn_mirror 参数，用于在构建时动态插入镜像源配置
def stage_build_context(assignment_dir: Path, build_dir: Path, dockerfile_src: Path, use_cn_mirror: bool = False) -> Path:
    remove_dir_if_exists(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    copy_tree(assignment_dir / "src", build_dir, EXCLUDE_NAMES)

    # Ensure Dockerfile present
    dockerfile_dst = build_dir / "Dockerfile"
    if not dockerfile_src.exists():
        raise FileNotFoundError(f"Dockerfile not found: {dockerfile_src}")
    shutil.copy2(dockerfile_src, dockerfile_dst)

    # 如果检测到在中国，动态插入 pip 镜像源配置到 Dockerfile
    if use_cn_mirror:
        dockerfile_content = dockerfile_dst.read_text(encoding="utf-8")
        lines = dockerfile_content.splitlines()
        
        # 查找第一个 pip install 命令的位置，在其之前插入镜像源配置
        insert_index = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("RUN") and "pip" in stripped.lower() and ("install" in stripped.lower() or "pip3" in stripped.lower()):
                insert_index = i
                break
        
        # 只有当找到 pip install 命令时才插入镜像源配置
        if insert_index is not None:
            mirror_config = [
                "",
                "# Auto-configured pip mirror for CN region (inserted by build_image.py)",
                "RUN printf '[global]\\nindex-url=https://pypi.tuna.tsinghua.edu.cn/simple\\n' > /etc/pip.conf && \\",
                "    echo 'Using CN mirror: https://pypi.tuna.tsinghua.edu.cn/simple'",
                "",
            ]
            lines[insert_index:insert_index] = mirror_config
            # Find the last USER command and insert cleanup command before it
            user_index = None
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip().startswith("USER"):
                    user_index = i
                    break
            
            # Insert the cleanup command before USER, or append to the end if no USER command is found
            cleanup_cmd = "RUN rm -f /etc/pip.conf"
            if user_index is not None:
                lines.insert(user_index, cleanup_cmd)
                lines.insert(user_index, "")
            else:
                lines += ["", cleanup_cmd]
            dockerfile_dst.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print("Inserted pip mirror configuration into Dockerfile")

    # Ensure Dockerfile not copied into image via COPY . by writing .dockerignore
    dockerignore_path = build_dir / ".dockerignore"
    dockerignore_contents = """
Dockerfile
.git
.DS_Store
build
metadata
""".lstrip()
    dockerignore_path.write_text(dockerignore_contents, encoding="utf-8")

    return build_dir


@contextmanager
def process_safe_lock(lock_file: Path):
    """
    :param lock_file: .lock文件路径
    """
    import errno
    lock_fd = None
    try:
        # 原子创建.lock文件，实现锁抢占
        lock_fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL)
        print(f"Lock file {lock_file} created {lock_fd}, process {os.getpid()} acquired the lock")
        os.close(lock_fd)
        yield  # 执行受保护的业务逻辑
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise  # 非文件已存在异常，正常抛出
        else:
            print(f"Lock file {lock_file} exists, process {os.getpid()} failed to acquire the lock")
            raise PermissionError(f"锁文件 {lock_file} 已存在，无法获取锁（其他进程正在运行）")
    finally:
        # 释放锁：关闭文件描述符 + 删除.lock文件
        if lock_fd is not None:
            try:
                os.remove(lock_file)
            except OSError:
                pass
    
def run_docker_build(build_dir: Path, image: str, tag: str) -> int:
    dockerfile_path = build_dir / "Dockerfile"
    cmd = [
        "docker",
        "build",
        "--no-cache",
        "--progress=plain",
        "--platform",
        "linux/amd64",
        "-t",
        f"{image}:{tag}",
        "-f",
        str(dockerfile_path),
        str(build_dir),
    ]
    # Stream output directly to the console
    return subprocess.call(cmd)


def run_docker_push(image: str, tag: str) -> int:
    cmd = [
        "docker",
        "push",
        f"{image}:{tag}",
    ]
    return subprocess.call(cmd)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    # assignment_dir = Path("tasks/" + args.assignment_dir).resolve()
    assignment_dir = get_task_dir(args.assignment_dir)
    if not assignment_dir.exists() or not assignment_dir.is_dir():
        print(f"Error: assignment_dir not found: {assignment_dir}", file=sys.stderr)
        return 2

    homework_name = assignment_dir.name.replace(" ", "-").lower()
    default_image = get_default_image_name(homework_name)
    if args.registry != DOCKER_REGISTRY or args.namespace != DOCKER_NAMESPACE:
        default_image = f"{args.registry.rstrip('/')}/{args.namespace}/{homework_name}"
    image = args.image or default_image
    tag = args.tag

    dockerfile_src = (
        Path(args.dockerfile).resolve()
        if args.dockerfile
        else assignment_dir / "metadata" / "Dockerfile"
    )

    # 检测国家，如果在中国则启用国内镜像源

    if args.use_pip_mirror:
        country = detect_country()
        use_cn_mirror = country == "CN"
        if country:
            print(f"Detected country: {country}, using CN mirror: {use_cn_mirror}")
        else:
            print("Could not detect country, using default PyPI source")
    else:
        use_cn_mirror = False

    check_cmd = ["docker", "image", "inspect", f"{image}:{tag}"]
    check_result = subprocess.run(check_cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if check_result.returncode == 0 and not args.force:
        print(f"[{image}] 已存在最新镜像，跳过构建")
    else:
        build_dir = get_task_build_dir(args.assignment_dir)
        if args.lock:
            try:
                BUILD_ROOT.mkdir(parents=True, exist_ok=True)
                lock_file = BUILD_ROOT / f"{args.assignment_dir}.lock"
                with process_safe_lock(lock_file):
                    build_dir = stage_build_context(
                        assignment_dir, build_dir, dockerfile_src, use_cn_mirror=use_cn_mirror
                    )
                    ret = run_docker_build(build_dir, image, tag)
            except PermissionError as e:
                # wait until lock released
                while lock_file.exists():
                    time.sleep(1)
                    print(f"Lock file {lock_file} exists, waiting...")
                ret = subprocess.run(check_cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL).returncode
            except Exception as e:
                print(f"Error: {e}")
                ret = 1
        else:
            build_dir = stage_build_context(
                assignment_dir, build_dir, dockerfile_src, use_cn_mirror=use_cn_mirror
            )
            ret = run_docker_build(build_dir, image, tag)
        status = "SUCCESS" if ret == 0 else "FAILURE"
        message = (
            f"[{status}] Docker build for '{assignment_dir.name}'\n"
            f"Image: {image}:{tag}\n"
            f"Platform: linux/amd64\n"
        )
        print(message)

        if ret != 0:
            return ret
        
    if not args.push:
        print(f"\nImage {image}:{tag} is available locally. Skipping push by default.")
        return 0

    print(f"\nStart pushing: {image}:{tag}\n")
    push_ret = run_docker_push(image=image, tag=tag)
    push_status = "SUCCESS" if push_ret == 0 else "FAILURE"
    push_msg = f"[{push_status}] Docker push {image}:{tag}"
    print(push_msg)
    return push_ret


if __name__ == "__main__":
    sys.exit(main())
