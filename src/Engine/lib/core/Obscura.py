from os import name as os_name
from pathlib import Path
import subprocess
from subprocess import Popen, DEVNULL, TimeoutExpired
from shutil import which
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from weakref import WeakSet
from contextlib import suppress

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
    def kill_process_on_port(port: int) -> None:
        """Kill any lingering process or child process listening on the given port across Windows, macOS, and Linux."""
        try:
            import psutil
            killed_pids: set[int] = set()

            # 1. Try system-wide net_connections (works on Windows/Linux; may raise AccessDenied on macOS without root)
            with suppress(psutil.AccessDenied, Exception):
                for conn in psutil.net_connections(kind="inet"):
                    if conn.laddr and conn.laddr.port == port and conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            logger.warning(f"Killing lingering process {proc.name()} (PID: {conn.pid}) on port {port}")
                            for child in proc.children(recursive=True):
                                with suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                                    child.kill()
                            proc.kill()
                            killed_pids.add(conn.pid)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass

            # 2. Fallback for macOS / non-root POSIX: inspect user processes matching obscura --port <port> or per-process connections
            if not killed_pids:
                port_str = str(port)
                for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                    with suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                        cmdline = proc.info.get("cmdline") or []
                        name = (proc.info.get("name") or "").lower()
                        is_matching_obscura = "obscura" in name and port_str in cmdline
                        has_port_conn = False
                        if not is_matching_obscura:
                            with suppress(psutil.AccessDenied, psutil.NoSuchProcess, Exception):
                                for conn in proc.net_connections(kind="inet"):
                                    if conn.laddr and conn.laddr.port == port:
                                        has_port_conn = True
                                        break
                        if is_matching_obscura or has_port_conn:
                            logger.warning(f"Killing lingering process {proc.info.get('name')} (PID: {proc.pid}) on port {port}")
                            for child in proc.children(recursive=True):
                                with suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                                    child.kill()
                            proc.kill()
        except Exception as e:
            logger.debug(f"Error checking lingering connections on port {port}: {e}")

    def spawn_instance(self, context: StormContext) -> int:
        retries: int = 0
        while retries < 20:
            if hasattr(context, "freed_obscura_ports") and context.freed_obscura_ports:
                port = context.freed_obscura_ports.pop(0)
            else:
                port = context.obscura_current_port
                context.obscura_current_port += 1

            if self.is_port_in_use(port):
                logger.warning(f"Port {port} is in use. Trying next port.")
                retries += 1
                continue

            cmd: list[str] = [self.obscura_path or "obscura", "serve", "--port", f"{port}"]
        
            kwargs: dict = {}    
            
            if os_name == "nt":
                detached = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
                new_group = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
                kwargs["creationflags"] = detached | new_group
            else:
                kwargs["start_new_session"] = True
                
            process: Popen = Popen(
                cmd,
                stdout=DEVNULL,
                stderr=DEVNULL,
                **kwargs
            )

            # Wait for Obscura to start listening on the port
            is_ready: bool = False
            for _ in range(50):
                if process.poll() is not None:
                    break
                if self.is_port_in_use(port):
                    is_ready = True
                    break
                sleep(0.1)

            if is_ready:
                logger.info(f"Obscura instance started on port {port} (PID: {process.pid}).")
                self.processes[port] = process
                return port

            exit_code: int | None = process.poll()
            logger.error(f"Failed to start Obscura instance on port {port} (Exit code: {exit_code}). Retrying with next port.")
            if exit_code is None:
                try:
                    process.kill()
                    process.wait(timeout=1)
                except Exception:
                    pass
            retries += 1

        raise RuntimeError("Failed to spawn Obscura instance after 20 retries.")

    def stop_instance(self, port: int, context: StormContext | None = None) -> None:
        process = self.processes.pop(port, None)
        if process and process.poll() is None:
            logger.debug(f"Terminating Obscura process on port {port} (PID: {process.pid})")
            try:
                # Terminate child processes first (e.g. Chrome instances)
                try:
                    import psutil
                    parent = psutil.Process(process.pid)
                    children = parent.children(recursive=True)
                    for child in children:
                        with suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                            child.terminate()
                except Exception:
                    pass

                process.terminate()
                process.wait(timeout=2)
            except TimeoutExpired:
                logger.warning(f"Obscura process on port {port} timed out; killing...")
                try:
                    import psutil
                    parent = psutil.Process(process.pid)
                    for child in parent.children(recursive=True):
                        with suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                            child.kill()
                except Exception:
                    pass
                process.kill()
                process.wait(timeout=1)
            except Exception as e:
                logger.error(f"Error terminating Obscura process on port {port}: {e}")

        # Ensure any process holding the port is freed
        if self.is_port_in_use(port):
            sleep(0.2)
            if self.is_port_in_use(port):
                self.kill_process_on_port(port)

        if context and hasattr(context, "freed_obscura_ports"):
            if port not in context.freed_obscura_ports:
                context.freed_obscura_ports.append(port)

    @classmethod
    def kill_all(cls) -> None:
        """Terminate every Obscura process spawned by this app (used on app exit; sync, safe to call anywhere)."""
        for obscura in list(cls._instances):
            with suppress(Exception):
                obscura.cleanup()

    def cleanup(self) -> None:
        if not self.processes:
            return
        logger.info(f"Cleaning up {len(self.processes)} Obscura process(es)...")
        for port in list(self.processes.keys()):
            self.stop_instance(port)
        self.processes.clear()
        logger.info("Obscura cleanup completed")

    def __del__(self):
        with suppress(Exception):
            self.cleanup()

__all__: list[str] = ['Obscura']
