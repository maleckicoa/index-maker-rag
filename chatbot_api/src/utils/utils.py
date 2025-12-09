import os
import sys
import psutil
import subprocess
import socket

import asyncio
from dotenv import set_key

def async_retry(max_retries: int=3, delay: int=1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    print(f"Attempt {attempt} failed: {str(e)}")
                    await asyncio.sleep(delay)

            raise ValueError(f"Failed after {max_retries} attempts")

        return wrapper

    return decorator



def set_llm(query, env_file_path):
    set_key(env_file_path, "INDEX_QA_MODEL", "gpt-4o-mini" , quote_mode='never')
    set_key(env_file_path, "INDEX_CYPHER_MODEL", "gpt-4o-mini" , quote_mode='never')

    if "special" in query.lower():
        set_key(env_file_path, "INDEX_QA_MODEL", "gpt-4o", quote_mode='never')
    if len(query) > 500:
        set_key(env_file_path, "INDEX_CYPHER_MODEL", "gpt-4o" , quote_mode='never')




def restart_application():
    """Restart the current Python application."""
    print("Restarting application...")
    os.execv(sys.executable, [sys.executable] + sys.argv)


def find_process_on_port(port):
    """
    Find the process ID (PID) of the process using the specified port.
    """
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Manually check connections for each process
            for conn in proc.connections(kind="inet"):  # 'inet' is for TCP/UDP
                if conn.laddr.port == port:
                    print(f"Found process {proc.info['pid']} using port {port}")
                    return proc.info['pid']
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            # Ignore processes we can't access
            continue
    return None



def kill_process_on_port(port):
    """
    Kill the process occupying the specified port.
    """
    pid = find_process_on_port(port)
    if pid:
        print(f"Killing process {pid} on port {port}...")
        try:
            os.kill(pid, 9)  # Force kill
            print(f"Process {pid} killed.")
        except Exception as e:
            print(f"Error killing process {pid}: {e}")
    else:
        print(f"No process found on port {port}.")


def free_port(port):
    """
    Ensure the port is freed by binding and closing it.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", port))
            print(f"Port {port} freed.")
        except OSError as e:
            print(f"Failed to free port {port}: {e}")


def restart_uvicorn(port):
    """
    Restart uvicorn on the specified port.
    """
    command = [
        sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", f"--port={port}"
    ]
    print(f"Starting uvicorn with command: {' '.join(command)}")
    subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

