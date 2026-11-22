import asyncio
from http.client import HTTPConnection
from json import loads
from os import name as os_name
from pathlib import Path
import subprocess
from subprocess import Popen, DEVNULL, TimeoutExpired
from shutil import which
from socket import socket, AF_INET, SOCK_STREAM
from weakref import WeakSet
from contextlib import suppress

import psutil

from .StormContext import StormContext
from logging import getLogger, Logger

logger: Logger = getLogger(f"streamstorm.{__name__}")

class Obscura:
    _instances: "WeakSet[Obscura]" = WeakSet()

    def __init__(self):
        Obscura._instances.add(self)
        self.obscura_present: bool = True
        self.processes: dict[int, Popen] = {}
        self.obscura_path: str | None = self._resolve_obscura_binary()
        
        if not self.obscura_path:  
            self.obscura_present: bool = False
            logger.error("Obscura not found in PATH. Please ensure Obscura is installed and added to your system's PATH.")
            raise RuntimeError("Obscura not installed. Install from https://docs.obscura.sh/quickstart/installation and then start storm again.")

    @staticmethod
    def _resolve_obscura_binary() -> str | None:
        """Resolve the Obscura binary across Windows, macOS, and Linux."""
        found = which("obscura")
        if found:
            return found

        home = Path.home()
        if os_name == "nt":
            candidates = [
                Path("C:/Utils/obscura.exe"),
                home / ".local" / "bin" / "obscura.exe",
                home / ".cargo" / "bin" / "obscura.exe",
                home / "AppData" / "Local" / "Programs" / "obscura" / "obscura.exe",
            ]
        else:
            candidates = [
                home / ".local" / "bin" / "obscura",
                home / ".cargo" / "bin" / "obscura",
                Path("/usr/local/bin/obscura"),
                Path("/opt/homebrew/bin/obscura"),
                Path("/usr/bin/obscura"),
            ]

        for candidate in candidates:
            with suppress(Exception):
                if candidate.is_file():
                    return str(candidate)
        return None
        
    @staticmethod
    def is_port_in_use(port: int) -> bool:
        with socket(AF_INET, SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0
        
    @staticmethod
    def _cdp_ready(port: int) -> bool:
        conn: HTTPConnection | None = None
        try:
            conn = HTTPConnection("127.0.0.1", port, timeout=1)
            conn.request("GET", "/json/version")
            response = conn.getresponse()
            if response.status != 200:
                return False
            payload = loads(response.read())
            return isinstance(payload, dict) and bool(payload.get("webSocketDebuggerUrl"))
        except Exception:
            return False
        finally:
            if conn is not None:
                with suppress(Exception):
                    conn.close()

    @staticmethod
    def _terminate_process_tree(process: Popen, timeout: float = 2) -> None:
        children: list[psutil.Process] = []
        with suppress(Exception):
            children = psutil.Process(process.pid).children(recursive=True)

        for child in children:
            with suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                child.terminate()

        process.terminate()
        try:
            process.wait(timeout=timeout)
        except TimeoutExpired:
            logger.warning(f"Obscura process (PID: {process.pid}) timed out; killing...")
            process.kill()
            process.wait(timeout=1)

        with suppress(Exception):
            _, alive = psutil.wait_procs(children, timeout=1)
            for child in alive:
                with suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                    child.kill()

    async def spawn_instance(self, context: StormContext) -> int:
        retries: int = 0
        while retries < 20:
            if hasattr(context, "freed_obscura_ports") and context.freed_obscura_ports:
                port = context.freed_obscura_ports.pop(0)
            else:
                port = context.obscura_current_port
                context.obscura_current_port += 1

            if await asyncio.to_thread(self.is_port_in_use, port):
                logger.warning(f"Port {port} is in use. Trying next port.")
                retries += 1
                continue

            cmd: list[str] = [
                self.obscura_path or "obscura",
                "--v8-flags=--max-old-space-size=32",
                "serve",
                "--port",
                f"{port}",
                "--quiet",
            ]
        
            kwargs: dict = {}    
            
            if os_name == "nt":
                detached = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
                new_group = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
                kwargs["creationflags"] = detached | new_group
            else:
                kwargs["start_new_session"] = True
                
            try:
                process: Popen = Popen(
                    cmd,
                    stdout=DEVNULL,
                    stderr=DEVNULL,
                    **kwargs
                )
            except OSError as e:
                raise RuntimeError(f"Failed to launch Obscura on port {port}: {e}") from e

            is_ready: bool = False
            for _ in range(50):
                if process.poll() is not None:
                    break
                if await asyncio.to_thread(self.is_port_in_use, port):
                    if process.poll() is not None:
                        break
                    if await asyncio.to_thread(self._cdp_ready, port) and process.poll() is None:
                        is_ready = True
                        break
                await asyncio.sleep(0.1)

            if is_ready:
                logger.info(f"Obscura instance started on port {port} (PID: {process.pid}).")
                self.processes[port] = process
                return port

            exit_code: int | None = process.poll()
            logger.error(f"Failed to start Obscura instance on port {port} (Exit code: {exit_code}). Retrying with next port.")
            if exit_code is None:
                with suppress(Exception):
                    await asyncio.to_thread(self._terminate_process_tree, process, 1)
            retries += 1

        raise RuntimeError("Failed to spawn Obscura instance after 20 retries.")

    def _stop_instance_sync(self, port: int, context: StormContext | None = None) -> None:
        process = self.processes.pop(port, None)
        if process is None:
            return

        if process.poll() is None:
            logger.debug(f"Terminating Obscura process on port {port} (PID: {process.pid})")
            try:
                self._terminate_process_tree(process)
            except Exception as e:
                logger.error(f"Error terminating Obscura process on port {port}: {e}")

        if context and hasattr(context, "freed_obscura_ports"):
            if port not in context.freed_obscura_ports:
                context.freed_obscura_ports.append(port)

    async def stop_instance(self, port: int, context: StormContext | None = None) -> None:
        await asyncio.to_thread(self._stop_instance_sync, port, context)

    @classmethod
    def kill_all(cls) -> None:
        """Terminate every Obscura process spawned by this app (used on app exit; sync, safe to call anywhere)."""
        for obscura in list(cls._instances):
            with suppress(Exception):
                obscura.cleanup_sync()

    def cleanup_sync(self) -> None:
        if not self.processes:
            return
        logger.info(f"Cleaning up {len(self.processes)} Obscura process(es)...Sync")
        for port in list(self.processes.keys()):
            self._stop_instance_sync(port)
        self.processes.clear()
        logger.info("Obscura sync cleanup completed")

    async def cleanup(self) -> None:
        if not self.processes:
            return
        logger.info(f"Cleaning up {len(self.processes)} Obscura process(es)...Async")
        for port in list(self.processes.keys()):
            await self.stop_instance(port)
        self.processes.clear()
        logger.info("Obscura async cleanup completed")

    def __del__(self):
        with suppress(Exception):
            self.cleanup_sync()

__all__: list[str] = ['Obscura']
