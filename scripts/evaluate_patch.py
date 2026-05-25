#!/usr/bin/env python3
from __future__ import annotations

import argparse
from loguru import logger
from pathlib import Path
from src.runtime.local_docker_container_runtime import LocalDockerContainerRuntime
from src.config import get_test_override_dir
from src.task.bench_task import BenchTask


def apply_git_patch_in_container(runtime: LocalDockerContainerRuntime, repo_root: str, patch_path: Path) -> None:
    if patch_path.exists() and patch_path.stat().st_size > 0:
        dest = "/tmp/patch.diff"
        runtime.transfer_file(patch_path, dest, to_container=True)
        # Use git apply with binary support
        # --3way: Use 3-way merge when possible for better conflict resolution
        # --ignore-whitespace: Be tolerant of whitespace differences
        ret, code = runtime.execute(input=f"cd {repo_root} && git apply --3way --ignore-whitespace {dest}")
        if isinstance(ret, bytes):
            ret_str = ret.decode('utf-8', errors='replace')
        else:
            ret_str = str(ret)
        
        if code != 0:
            logger.warning(f"git apply failed (code={code}), trying with --reject:\n{ret_str}")
            # If normal apply fails, try with --reject to apply what we can
            ret2, code2 = runtime.execute(input=f"cd {repo_root} && git apply --reject --ignore-whitespace {dest}")
            if isinstance(ret2, bytes):
                ret2_str = ret2.decode('utf-8', errors='replace')
            else:
                ret2_str = str(ret2)
            logger.info(f"git apply --reject output (code={code2}):\n{ret2_str}")
            
            # Check if there are any .rej files (rejected hunks)
            rej_check, _ = runtime.execute(input=f"cd {repo_root} && find . -name '*.rej' -type f")
            if isinstance(rej_check, bytes):
                rej_check_str = rej_check.decode('utf-8', errors='replace').strip()
            else:
                rej_check_str = str(rej_check).strip()
            if rej_check_str:
                logger.warning(f"Found rejected hunks:\n{rej_check_str}")
        else:
            logger.info(f"git apply succeeded (code={code})")

def archive_repo_to_zip(runtime: LocalDockerContainerRuntime, repo_root: str, output_path: Path) -> None:
    zip_path = "/tmp/testbed.zip"
    # Zip the repo root, excluding .git directory
    ret, code = runtime.execute(input=f"sudo apt-get update && sudo apt-get install -y zip && cd {repo_root} && zip -r {zip_path} . -x '*.git*'", timeout=600)
    if code != 0:
        logger.error(f"Failed to zip repository (code={code}):\n{ret.decode('utf-8', errors='replace') if isinstance(ret, bytes) else str(ret)}")
        return
    
    # Transfer the zip file from container to host
    runtime.transfer_file(zip_path, output_path, to_container=False)
    logger.info(f"Repository zipped and saved to {output_path}")

    # Clean up the zip file in the container
    runtime.execute(input=f"rm {zip_path}")


def restore_testoverrides_in_container(runtime: LocalDockerContainerRuntime, repo_root: str, task_name: str) -> None:
    host_override_dir = get_test_override_dir(task_name)
    
    if host_override_dir.exists():
        for p in host_override_dir.rglob('*'):
            if p.is_dir() or p.name == '.files':
                continue
            rel = p.relative_to(host_override_dir)
            dst_dir = f"{repo_root}{'' if rel.parent.as_posix() == '.' else '/' + rel.parent.as_posix()}"
            runtime.execute(input=f"mkdir -p {dst_dir}")
            runtime.transfer_file(p, f"{dst_dir}/{rel.name}", to_container=True)


def run_tests_in_container(runtime: LocalDockerContainerRuntime, src_dir: str) -> bool:
    cmd = f"bash -lc 'cd {src_dir} && bash test.sh'"
    # import IPython; IPython.embed()
    # print(runtime.execute(input="cat imdb.cc")[0])
    out, code = runtime.execute(input=cmd, timeout=1800)
    if isinstance(out, bytes):
        out_str = out.decode('utf-8', errors='replace')
    else:
        out_str = str(out)
    print(out_str)
    return code == 0




def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task_name")
    ap.add_argument("log_tag", type=int, help="int num of attempt (e.g., 0, 1, ... , k-1)")
    ap.add_argument(
        "--archive-testbed",
        action="store_true",
        help="Archive the evaluated /testbed directory to testbed.zip in the log directory",
    )
    args = ap.parse_args()

    task = BenchTask.from_name(args.task_name)
    log_dir = task.to_log_dir(args.log_tag)
    assert log_dir.exists(), f"log not found: {log_dir}"

    image_name = task.to_image_name()
    rt = LocalDockerContainerRuntime(image_name=image_name)
    rt.start()
    repo_root = "/testbed"
    rt.execute(input=f"cd {repo_root} && rm -rf .base_commit")
    apply_git_patch_in_container(rt, repo_root, log_dir / "patch")
    restore_testoverrides_in_container(rt, repo_root, args.task_name)
    if args.archive_testbed:
        archive_repo_to_zip(rt, repo_root, log_dir / "testbed.zip")
    ok = run_tests_in_container(rt, repo_root)
    rt.stop()
    print("\nFailed" if not ok else "\nPass")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
