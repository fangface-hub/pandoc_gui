# -*- coding: utf-8 -*-
"""subprocess extensions."""
import subprocess
import sys


def terminate_process(proc: subprocess.Popen,
                      logger=None,
                      timeout: float = 5.0) -> None:
    """
    Safely terminate a subprocess according to the platform.
    On Windows, attempts to terminate the process tree using taskkill.
    On failure or other OSes, uses terminate/kill.

    :param proc: The Popen object to be terminated
    :param logger: Optional logger for logging
    :param timeout: Timeout in seconds to wait for termination
    """
    if proc.poll() is not None:
        return  # 既に終了
    try:
        if sys.platform.startswith("win"):
            try:
                result = subprocess.run(
                    ["taskkill", "/F", "/T", "/PID",
                     str(proc.pid)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False)
                if logger:
                    logger.info(
                        f"process_tree_terminated: {result.stdout.strip()}")
                if result.returncode != 0 and logger:
                    logger.warning(f"taskkill_exit_code: {result.returncode}, "
                                   f"{result.stderr.strip()}")
            except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as e:
                if logger:
                    logger.warning(f"taskkill_failed: {e}")
                try:
                    proc.terminate()
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    proc.kill()
        else:
            try:
                proc.terminate()
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                if logger:
                    logger.warning("child_process_force_kill")
                proc.kill()
    except (OSError, subprocess.TimeoutExpired) as e:
        if logger:
            logger.error(f"terminate_process_error: {e}")
