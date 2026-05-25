#!/usr/bin/env python3
# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: Apache-2.0
"""
每个attempt都是一个不断派发子进程的线程
一个task进行多次attempt时，首先由某个attempt把docker setup好，做好冷启动检查，然后每个attempt各自独立的运行
派发的子进程包括：run_agent/evaluate_patch等
子进程把stdout和stderr输出到文件中，防止管道缓冲区堵塞导致子进程卡死
为了正确响应ctrl+C，用非阻塞轮询的方式等待子进程
设置一个全局的threading.Event，触发时用terminate+kill优雅结束
"""
import os
import subprocess
import sys
import json
import logging
import time
import threading
from pathlib import Path
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.logging import RichHandler
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque, defaultdict

from src.config import OUTPUT_ROOT, REPORTS_DIR, TASKS_DIR, get_task_dir, get_task_log_dir, get_report_path
from src.task.bench_task import BenchTask

log_capture = deque(maxlen=10)

# Global Stop Event for graceful shutdown
STOP_EVENT = threading.Event()

class CaptureHandler(logging.Handler):
    def emit(self, record):
        log_capture.append(self.format(record))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='[%X]',
    handlers=[RichHandler(rich_tracebacks=True), CaptureHandler()]
)
logger = logging.getLogger("CSBench")
force_build = False
class TaskSharedState:
    """Manages shared state for a task across multiple attempts."""
    def __init__(self):
        self.lock = threading.Lock()
        self.setup_done = threading.Event()
        self.setup_success = False
        self.setup_info = {}
        self.is_setting_up = False

class TaskRunner:
    def __init__(self, task_name, attempt_id=0, capture=True, shared_state=None):
        self.task_name = task_name
        self.attempt_id = attempt_id
        self.capture = capture
        self.report = {}
        self._status = "pending"
        self.status_time = datetime.now()
        self.start_time = None
        self.shared_state = shared_state

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        self.status_time = datetime.now()

    def run_command_with_timing_no_capture(self, cmd: list, step_name: str) -> tuple:
        """执行命令并记录执行时间和结果"""
        self.status = f"running: {step_name}"
        if self.start_time is None:
            self.start_time = datetime.now()
        start_time = time.time()
        
        # Prepare log files

        process = subprocess.run(
            cmd, 
            text=True,
            stdin=subprocess.DEVNULL,
            capture_output=False,
        )
        returncode = process.returncode
        end_time = time.time()
        duration = end_time - start_time
        
        info = {
            "command": ' '.join(cmd),
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "returncode": returncode,
            "stdout": "",
            "stderr": ""
        }
        
        self.status = f"{step_name}: {returncode}"
        return not returncode, info
    
    def run_command_with_timing(self, cmd: list, step_name: str) -> tuple:
        """执行命令并记录执行时间和结果"""
        if not self.capture:
            return self.run_command_with_timing_no_capture(cmd, step_name)
        
        self.status = f"running: {step_name}"
        if self.start_time is None:
            self.start_time = datetime.now()
        start_time = time.time()
        
        # Prepare log files
        log_dir = get_task_log_dir(self.task_name, self.attempt_id)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        stdout_path = log_dir / f"{step_name}.out"
        stderr_path = log_dir / f"{step_name}.err"
        
        stdout_f = open(stdout_path, "w")
        stderr_f = open(stderr_path, "w")
        
        returncode = -1
        stdout_content = ""
        stderr_content = ""
        
        try:
            process = subprocess.Popen(
                cmd, 
                stdout=stdout_f, 
                stderr=stderr_f,
                text=True, 
                stdin=subprocess.DEVNULL
            )
            
            while process.poll() is None:
                if STOP_EVENT.is_set():
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    break
                time.sleep(0.1)
                
            returncode = process.returncode
        except KeyboardInterrupt:
            ### 可能是直接使用Taskrunner而非通过线程使用
            logger.info(f"[{self.task_name}] 收到ctrl+C信号，尝试优雅结束")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            returncode = -1
        except Exception as e:
            logger.error(f"Process execution failed: {e}")
            returncode = -1
        finally:
            if not stdout_f.closed: stdout_f.close()
            if not stderr_f.closed: stderr_f.close()
            
        try:
            if stdout_path.exists():
                with open(stdout_path, "r") as f:
                    stdout_content = f.read()
            if stderr_path.exists():
                with open(stderr_path, "r") as f:
                    stderr_content = f.read()
        except Exception as e:
            logger.error(f"Failed to read log files: {e}")

        end_time = time.time()
        duration = end_time - start_time
        
        info = {
            "command": ' '.join(cmd),
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "returncode": returncode,
            "stdout": stdout_content,
            "stderr": stderr_content
        }
        
        self.status = f"{step_name}: {returncode}"
        return not returncode, info

    def build_docker_image(self) -> bool:
        """构建Docker镜像"""
        logger.debug(f"[{self.task_name}] 开始构建Docker镜像")
        build_cmd = [sys.executable, "-u", "-m", "scripts.build_image", self.task_name]
        if force_build:
            build_cmd.append("--force")
        
        success, info = self.run_command_with_timing(build_cmd, "1.docker_build")
        
        self.report["docker_build"] = success
        self.report["docker_build_info"] = info
        
        if not success:
            logger.error(f"[{self.task_name}] 构建镜像失败，返回码: {info['returncode']}")
        else:
            logger.debug(f"[{self.task_name}] Docker镜像构建成功")
        
        return success

    def run_coldstart_test(self) -> bool:
        """运行Coldstart测试"""
        logger.debug(f"[{self.task_name}] 开始Coldstart测试")
        import uuid
        image_name = BenchTask.from_name(self.task_name).to_image_name()
        # Check sudo
        docker_cmd = [
            "docker", "run", "--rm", "--platform", "linux/amd64", 
            "--name", f"csbench-test-{self.task_name}-{uuid.uuid4().hex[:8]}", image_name,
            "which","sudo"
        ]
        success, info = self.run_command_with_timing(docker_cmd, "2.coldstart")
        if not success:
            logger.error(f"[{self.task_name}] 检查sudo失败，返回码: {info['returncode']}")
            return False
            
        # Run test.sh
        docker_cmd = [
            "docker", "run", "--rm", "--platform", "linux/amd64", 
            "--name", f"csbench-test-{self.task_name}-{uuid.uuid4().hex[:8]}", image_name,
            "bash","test.sh"
        ]
        def process_pytest_output(output: str) -> str:
            lines = output.splitlines()
            import re
            # F.FFFFFFFFFFF.F.F.FFFFFFF.                                               [100%]
            RE_OUTPUT = re.compile(r"^([F.Es]+)\s*(\[\d+%\])?$")
            output = ""
            for line in lines:
                m = RE_OUTPUT.match(line)
                if m:
                    output += m.group(1)
            return output
        
        success, info = self.run_command_with_timing(docker_cmd, "2.coldstart")
        coldstart = not success and process_pytest_output(info["stdout"])
        self.report["coldstart"] = coldstart
        self.report["coldstart_info"] = info
        
        if not coldstart:
            logger.warning(f"[{self.task_name}] docker run测试失败")
        else:
            logger.debug(f"[{self.task_name}] docker run测试成功，返回码: {info['returncode']}")
        
        return bool(coldstart)

    def ensure_setup(self) -> bool:
        """Ensure setup (build + coldstart) is done, using shared state if available."""
        if not self.shared_state:
            # No shared state, do it locally (legacy mode)
            if not self.report.get('docker_build'):
                if not self.build_docker_image(): return False
            if not self.report.get('coldstart'):
                if not self.run_coldstart_test(): return False
            return True

        # Check if setup is already done
        if self.shared_state.setup_done.is_set():
            if not self.shared_state.setup_success:
                self.status = "setup failed (shared)"
                return False
            # Copy shared setup info
            self.report.update(self.shared_state.setup_info)
            return True

        # Try to become the setup runner
        should_setup = False
        with self.shared_state.lock:
            if not self.shared_state.is_setting_up and not self.shared_state.setup_done.is_set():
                self.shared_state.is_setting_up = True
                should_setup = True
        
        if should_setup:
            try:
                # 1. Build
                if not self.report.get('docker_build'):
                    if not self.build_docker_image():
                        self.shared_state.setup_success = False
                        self.shared_state.setup_info = {
                            "docker_build": False,
                            "docker_build_info": self.report.get("docker_build_info")
                        }
                        self.shared_state.setup_done.set()
                        return False
                
                # 2. Coldstart
                if not self.report.get('coldstart'):
                    if not self.run_coldstart_test():
                        self.shared_state.setup_success = False
                        self.shared_state.setup_info = {
                            "docker_build": True,
                            "docker_build_info": self.report.get("docker_build_info"),
                            "coldstart": False,
                            "coldstart_info": self.report.get("coldstart_info")
                        }
                        self.shared_state.setup_done.set()
                        return False
                
                # Success
                self.shared_state.setup_success = True
                self.shared_state.setup_info = {
                    "docker_build": True,
                    "docker_build_info": self.report.get("docker_build_info"),
                    "coldstart": self.report.get("coldstart"), # pass or fail is ok, but here it means ran successfully
                    "coldstart_info": self.report.get("coldstart_info")
                }
                self.shared_state.setup_done.set()
                return True
            except Exception as e:
                logger.error(f"Setup failed with exception: {e}")
                self.shared_state.setup_success = False
                self.shared_state.setup_done.set()
                return False
        else:
            # Wait for setup
            self.status = "waiting for setup"
            while not self.shared_state.setup_done.is_set():
                if STOP_EVENT.is_set():
                    return False
                time.sleep(1)
            
            if not self.shared_state.setup_success:
                self.status = "setup failed (shared)"
                return False
                
            self.report.update(self.shared_state.setup_info)
            return True

    def run_agent_script(self) -> bool:
        """运行Agent脚本"""
        logger.debug(f"[{self.task_name}] 开始运行Agent (attempt {self.attempt_id})")
        log_tag = f"attempt{self.attempt_id}"
        run_agent_cmd = [sys.executable, "-u", "-m", "scripts.run_agent", "code_act_agent", self.task_name, log_tag]
        
        success, info = self.run_command_with_timing(run_agent_cmd, "3.run_agent")
        
        self.report["run_agent"] = success
        self.report["run_agent_info"] = info
        
        if not success:
            logger.error(f"[{self.task_name}] 运行agent失败 (attempt {self.attempt_id})，返回码: {info['returncode']}")
        else:
            logger.debug(f"[{self.task_name}] Agent运行成功 (attempt {self.attempt_id})")
        
        return success

    def evaluate_task_performance(self) -> bool:
        """评估任务性能"""
        logger.debug(f"[{self.task_name}] 开始评估任务 (attempt {self.attempt_id})")
        log_tag = self.attempt_id
        evaluate_cmd = [sys.executable, "-u", "-m", "scripts.evaluate_patch", self.task_name, str(log_tag)]
        
        _, info = self.run_command_with_timing(evaluate_cmd, "4.evaluate")
        
        success = info["stdout"].endswith("\nFailed\n") or info["stdout"].endswith("\nPass\n")

        self.report["evaluate"] = success
        self.report["evaluate_result"] = None if not success else info["stdout"].split("\n")[-2]
        self.report["evaluate_info"] = info
        
        if not success:
            logger.error(f"[{self.task_name}] 评估失败 (attempt {self.attempt_id})，返回码: {info['returncode']}")
        else:
            logger.debug(f"[{self.task_name}] 任务评估成功 (attempt {self.attempt_id})")
        
        return success

    def transform_conversation_history(self) -> bool:
        """转换对话记录"""
        logger.debug(f"[{self.task_name}] 开始转换对话记录 (attempt {self.attempt_id})")
        log_dir = get_task_log_dir(self.task_name, self.attempt_id)
        conv_path = log_dir / "conversation_history.json"
        transform_cmd = [sys.executable, "-u", "-m", "scripts.visualize_conversation", str(conv_path)]
        
        success, info = self.run_command_with_timing(transform_cmd, "5.transform")
        
        self.report["transform"] = success
        self.report["transform_info"] = info
        
        if not success:
            logger.error(f"[{self.task_name}] 转换失败 (attempt {self.attempt_id})，返回码: {info['returncode']}")
        else:
            logger.debug(f"[{self.task_name}] 对话记录转换成功 (attempt {self.attempt_id})")
        
        return success

    def run(self) -> dict:
        """执行单个任务的完整流程"""
        if STOP_EVENT.is_set():
            self.status = "cancelled"
            return self.report

        logger.info(f"[{self.task_name}] 开始执行任务 (attempt {self.attempt_id})")
        os.environ["TASK"] = self.task_name
        self.load_report()
        
        # 1. Setup Phase
        if not self.ensure_setup():
            self.dump_report()
            self.status = "error: " + self.status
            return self.report
            
        self.dump_report()
        
        # 2. Agent Execution
        if STOP_EVENT.is_set(): 
            self.status = "cancelled"
            return self.report

        if not self.report.get('run_agent'):
            if not self.run_agent_script():
                self.dump_report()
                self.status = "error: " + self.status
                return self.report

        self.dump_report()
        
        # 3. Post-processing & Evaluation
        if STOP_EVENT.is_set(): 
            self.status = "cancelled"
            return self.report

        if self.report.get('transform') is None:
            self.transform_conversation_history()
            self.dump_report()
            
        evaluate_info = self.report.get("evaluate_info") or {}
        if not self.report.get('evaluate') or 'Command timed out after 600' in evaluate_info.get('stdout', ''):
            self.evaluate_task_performance()
            self.dump_report()
            
        logger.info(f"[{self.task_name}] 任务运行完成 (attempt {self.attempt_id})")
        self.status = "completed"
        return self.report

    def load_report(self):
        """加载任务报告"""
        report_path = get_report_path(self.task_name, self.attempt_id)
        if report_path.exists():
            with open(report_path, "r") as f:
                self.report = json.load(f)
        else:
            self.report = {
                "task_name": self.task_name,
                "attempt_id": self.attempt_id,
                "docker_build": None,
                "coldstart": None,
                "run_agent": None,
                "evaluate": None,
                "transform": None,
                "evaluate_result": None
            }

    def dump_report(self):
        """保存任务报告"""
        report_path = get_report_path(self.task_name, self.attempt_id)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(self.report, f, indent=4)
        return self.report

def generate_layout(tasks_runners) -> Layout:
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(ratio=1, name="main"),
        Layout(name="footer", size=10)
    )
    
    table = Table(title="任务状态")
    table.add_column("任务名称", justify="left", style="cyan", no_wrap=True)
    table.add_column("运行ID", justify="left", style="cyan", no_wrap=True)
    table.add_column("状态", justify="left", style="magenta")
    table.add_column("启动时间", justify="left", style="green")
    table.add_column("状态更新时间", justify="left", style="yellow")
    
    # 限制显示的行数，防止太多
    MAX_ROWS = 40
    
    active_runners = sorted([r for r in tasks_runners if r.status != "completed" and "error" not in r.status], key=lambda x: (-x.status_time.timestamp(), x.task_name, x.attempt_id))
    error_runners = sorted([r for r in tasks_runners if "error" in r.status], key=lambda x: (x.task_name, x.attempt_id))
    completed_runners = [r for r in tasks_runners if r.status == "completed"]
    
    display_runners = active_runners + error_runners + completed_runners
    # 如果太多，优先显示活跃的
    if len(display_runners) > MAX_ROWS:
        display_runners = display_runners[:MAX_ROWS]

    for runner in display_runners:
        start_time_str = runner.start_time.strftime("%Y-%m-%d %H:%M:%S") if runner.start_time else "-"
        status_time_str = runner.status_time.strftime("%Y-%m-%d %H:%M:%S")
        table.add_row(runner.task_name, f"attempt{runner.attempt_id}", runner.status, start_time_str, status_time_str)
        
    header_text = Text(f"{os.environ.get('ENV_FILE', '.env')} | {datetime.now().ctime()} | Total: {len(tasks_runners)} | Active: {len(active_runners)} | Completed: {len(completed_runners)}", style="bold magenta", justify="center")
    log_panel = Panel(Text('\n'.join(log_capture), justify="left"), title="Logs", border_style="green")
    
    layout["header"].update(Panel(header_text))
    layout["main"].update(table)
    layout["footer"].update(log_panel)
    return layout

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='CSBench任务运行器')
    parser.add_argument('--log', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='日志级别 (默认: INFO)')
    parser.add_argument('-n', '--num-tasks', type=int, default=-1,
                        help='总任务数 (默认: -1, 表示所有任务)')
    parser.add_argument('-k', '--pass-k', type=int, default=1,
                        help='pass@k 评估参数 (默认: 1)')
    parser.add_argument('-x', type=int, default=8,
                        help='最大并发任务数 (默认: 8)')
    parser.add_argument('--task', type=str, default=None,
                        help='指定单个任务名称')
    parser.add_argument('--attempt-id', type=int, default=0,
                        help='尝试ID (用于pass@k评估)')
    parser.add_argument('--force-build', action='store_true', 
                        help='强制构建Docker镜像，即使已存在最新镜像')
    args = parser.parse_args()
    
    logger.setLevel(getattr(logging, args.log))
    logger.info(f"日志级别设置为: {args.log}")
    
    logger.info(f"CSBench根目录: {OUTPUT_ROOT}")
    force_build = args.force_build
    if args.task:
        # 模式匹配
        if args.task.startswith("[") and args.task.endswith("]"):
            tasks = args.task[1:-1].split(",")
            tasks = [task.strip() for task in tasks]
        else:
            tasks = [args.task]
        for task in tasks:
            task_dir = get_task_dir(task)
            if not task_dir.exists():
                logger.error(f"任务目录不存在: {task_dir}, tasks={tasks}")
                sys.exit(1)
    else:
        if not TASKS_DIR.exists():
            logger.error(f"任务目录不存在: {TASKS_DIR}")
            sys.exit(1)
        logger.info(f"开始扫描任务目录: {TASKS_DIR}")
        tasks = sorted([task.name for task in TASKS_DIR.iterdir() if task.is_dir()])
        logger.info(f"找到 {len(tasks)} 个任务")
        
        if args.num_tasks > 0:
            tasks = tasks[:args.num_tasks]
            logger.info(f"运行前 {args.num_tasks} 个任务")

    # 按任务分组管理 Shared State
    task_states = defaultdict(TaskSharedState)
    
    # 创建所有runners
    tasks_runners = []
    for task_name in tasks:
        shared_state = task_states[task_name]
        for i in range(args.pass_k):
            tasks_runners.append(TaskRunner(task_name, attempt_id=i, shared_state=shared_state))
    
    with Live(generate_layout(tasks_runners), refresh_per_second=2, transient=True) as live:
        with ThreadPoolExecutor(max_workers=args.x) as executor:
            # 提交所有独立的runner任务
            futures = {executor.submit(runner.run): runner for runner in tasks_runners}
            
            def cancel_all_futures(*args):
                logger.info("Stopping all tasks...")
                STOP_EVENT.set()
                # 不需要手动cancel futures，只要设置event，running的task会自己退出
                # 但未开始的future还是需要cancel
                for future in futures:
                    future.cancel()
                
            import signal
            signal.signal(signal.SIGINT, cancel_all_futures)
            
            while futures:
                # 检查任务状态
                done_futures = []
                for future in futures:
                    if future.done():
                        done_futures.append(future)
                
                for future in done_futures:
                    runner = futures.pop(future)
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Task {runner.task_name} attempt {runner.attempt_id} failed: {e}")
                
                live.update(generate_layout(tasks_runners))
                
                if STOP_EVENT.is_set() and not futures:
                    break
                    
                time.sleep(0.5)
                    
    logger.info("所有任务处理完成")
