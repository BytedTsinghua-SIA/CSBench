#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import subprocess
import sys
import time
from collections import defaultdict

from rich.live import Live
from concurrent.futures import ThreadPoolExecutor

import src.config as config
from src.config import get_task_dir

from run import TaskRunner, TaskSharedState, generate_layout, STOP_EVENT, logger


class DockerHubTaskRunner(TaskRunner):
    def __init__(
        self,
        *args,
        pull_policy: str,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.pull_policy = pull_policy

    def _image_exists_locally(self, image_ref: str) -> bool:
        check_cmd = ["docker", "image", "inspect", image_ref]
        r = subprocess.run(
            check_cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return r.returncode == 0

    def build_docker_image(self) -> bool:
        image_ref = config.get_default_image_ref(self.task_name)
        pull_policy = str(self.pull_policy)

        if pull_policy == "never":
            ok = self._image_exists_locally(image_ref)
            info = {
                "command": f"(skip pull, policy=never) image={image_ref}",
                "start_time": time.time(),
                "end_time": time.time(),
                "duration": 0.0,
                "returncode": 0 if ok else 1,
                "stdout": "",
                "stderr": "",
            }
            self.report["docker_build"] = ok
            self.report["docker_build_info"] = info
            if not ok:
                logger.error(f"[{self.task_name}] 本地不存在镜像且 pull_policy=never: {image_ref}")
            return ok

        if pull_policy == "if-missing" and self._image_exists_locally(image_ref):
            info = {
                "command": f"(skip pull, policy=if-missing) image={image_ref}",
                "start_time": time.time(),
                "end_time": time.time(),
                "duration": 0.0,
                "returncode": 0,
                "stdout": "",
                "stderr": "",
            }
            self.report["docker_build"] = True
            self.report["docker_build_info"] = info
        else:
            pull_cmd = ["docker", "pull", "--platform", "linux/amd64", image_ref]
            success, info = self.run_command_with_timing(pull_cmd, "1.docker_build")
            if not success and "unknown flag: --platform" in (info.get("stderr") or "").lower():
                pull_cmd = ["docker", "pull", image_ref]
                success, info = self.run_command_with_timing(pull_cmd, "1.docker_build")
            self.report["docker_build"] = success
            self.report["docker_build_info"] = info
            if not success:
                logger.error(f"[{self.task_name}] pull 镜像失败: {image_ref} (rc={info['returncode']})")
                return False

        self.report["image_ref"] = image_ref
        return True

    def run_coldstart_test(self) -> bool:
        info = {
            "command": "(skip coldstart) pull-docker mode",
            "start_time": time.time(),
            "end_time": time.time(),
            "duration": 0.0,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
        }
        self.report["coldstart"] = True
        self.report["coldstart_info"] = info
        return True


if __name__ == "__main__":
    import argparse
    import signal

    config.load_env()

    parser = argparse.ArgumentParser(description="CSBench 主入口（pull 镜像版本）")
    parser.add_argument("--log", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="日志级别 (默认: INFO)")
    parser.add_argument("-n", "--num-tasks", type=int, default=-1, help="总任务数 (默认: -1, 表示所有任务)")
    parser.add_argument("-k", "--pass-k", type=int, default=1, help="pass@k 评估参数 (默认: 1)")
    parser.add_argument("-x", type=int, default=8, help="最大并发任务数 (默认: 8)")
    parser.add_argument("--task", type=str, default=None, help="指定单个任务名称")
    parser.add_argument("--pull-policy", type=str, default="if-missing", choices=["always", "if-missing", "never"], help="镜像 pull 策略")
    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log))
    logger.info(f"日志级别设置为: {args.log}")
    logger.info(f"CSBench根目录: {config.OUTPUT_ROOT}")

    if args.task:
        if args.task.startswith("[") and args.task.endswith("]"):
            tasks = [t.strip() for t in args.task[1:-1].split(",")]
        else:
            tasks = [args.task]
        for task in tasks:
            task_dir = get_task_dir(task)
            if not task_dir.exists():
                logger.error(f"任务目录不存在: {task_dir}, tasks={tasks}")
                sys.exit(1)
    else:
        if not config.TASKS_DIR.exists():
            logger.error(f"任务目录不存在: {config.TASKS_DIR}")
            sys.exit(1)
        logger.info(f"开始扫描任务目录: {config.TASKS_DIR}")
        tasks = sorted([task.name for task in config.TASKS_DIR.iterdir() if task.is_dir()])
        logger.info(f"找到 {len(tasks)} 个任务")
        if args.num_tasks > 0:
            tasks = tasks[: args.num_tasks]
            logger.info(f"运行前 {args.num_tasks} 个任务")

    task_states = defaultdict(TaskSharedState)
    tasks_runners = []
    for task_name in tasks:
        shared_state = task_states[task_name]
        for i in range(args.pass_k):
            tasks_runners.append(
                DockerHubTaskRunner(
                    task_name,
                    attempt_id=i,
                    shared_state=shared_state,
                    pull_policy=args.pull_policy,
                )
            )

    def cancel_all_futures(*_args):
        logger.info("Stopping all tasks...")
        STOP_EVENT.set()

    signal.signal(signal.SIGINT, cancel_all_futures)

    with Live(generate_layout(tasks_runners), refresh_per_second=2, transient=True) as live:
        with ThreadPoolExecutor(max_workers=args.x) as executor:
            futures = {executor.submit(runner.run): runner for runner in tasks_runners}
            while futures:
                done = [f for f in futures if f.done()]
                for f in done:
                    runner = futures.pop(f)
                    try:
                        f.result()
                    except Exception as e:
                        logger.error(f"Task {runner.task_name} attempt {runner.attempt_id} failed: {e}")
                live.update(generate_layout(tasks_runners))
                if STOP_EVENT.is_set() and not futures:
                    break
                time.sleep(0.5)

    logger.info("所有任务处理完成")
