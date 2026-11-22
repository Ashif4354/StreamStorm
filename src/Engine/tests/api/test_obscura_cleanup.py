import asyncio
import itertools
import json
import socket
import subprocess
import sys
import threading
import time
from contextlib import suppress, contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import MagicMock, AsyncMock, patch

import psutil
import pytest

from lib.core.Obscura import Obscura
from lib.core.StreamStorm import StreamStorm
from lib.api.validation import StormData
from lib.core.StormContext import StormContext

SLEEPER = [sys.executable, "-c", "import time; time.sleep(120)"]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _make_obscura() -> Obscura:
    with patch("lib.core.Obscura.which", return_value="/usr/bin/obscura"):
        return Obscura()


def _is_gone(pid: int, timeout: float = 5.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if psutil.Process(pid).status() == psutil.STATUS_ZOMBIE:
                return True
        except psutil.NoSuchProcess:
            return True
        time.sleep(0.05)
    return False


def _storm_data(channels: list[int] | None = None) -> StormData:
    return StormData(
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        chat_url="https://www.youtube.com/live_chat?v=dQw4w9WgXcQ",
        messages=["hello"],
        subscribe=False,
        subscribe_and_wait=False,
        subscribe_and_wait_time=0,
        slow_mode=5,
        channels=channels or [1],
        background=False
    )


def _make_storm(channels: list[int] | None = None, engine: str = "obscura") -> StreamStorm:
    with patch.object(StreamStorm, "load_cookies", return_value={}), \
         patch.object(StreamStorm, "get_channel_url", return_value=("", False)), \
         patch("lib.core.StreamStorm.Profiles.__init__", return_value=None), \
         patch("lib.core.StreamStorm.settings") as mock_settings, \
         patch("lib.core.StreamStorm.Obscura") as MockObscuraCls:
        mock_settings.engine = engine
        mock_settings.login_method = "cookies"
        mock_obscura = MagicMock()
        mock_obscura.cleanup = AsyncMock()
        mock_obscura.spawn_instance = AsyncMock(return_value=9222)
        MockObscuraCls.return_value = mock_obscura
        return StreamStorm(_storm_data(channels))


def test_obscura_processes_dict_initialized():
    obs = _make_obscura()
    assert isinstance(obs.processes, dict)
    assert len(obs.processes) == 0


def test_obscura_binary_resolution_fallback_cross_platform():
    with patch("lib.core.Obscura.which", return_value=None), \
         patch("lib.core.Obscura.os_name", "posix"), \
         patch("lib.core.Obscura.Path.is_file", return_value=True):
        binary = Obscura._resolve_obscura_binary()
        assert binary is not None
        assert "obscura" in binary


def test_port_based_kill_helper_is_gone():
    assert not hasattr(Obscura, "kill_process_on_port")


def test_obscura_cleanup_terminates_all_real_processes():
    async def _run():
        obs = _make_obscura()
        procs = [subprocess.Popen(SLEEPER), subprocess.Popen(SLEEPER)]
        try:
            obs.processes[9222] = procs[0]
            obs.processes[9223] = procs[1]

            await obs.cleanup()

            assert len(obs.processes) == 0
            for proc in procs:
                assert proc.poll() is not None
        finally:
            for proc in procs:
                if proc.poll() is None:
                    proc.kill()
    asyncio.run(_run())


def test_obscura_stop_single_instance_frees_port_in_context():
    async def _run():
        obs = _make_obscura()
        ctx = StormContext()
        proc = subprocess.Popen(SLEEPER)
        try:
            obs.processes[9224] = proc
            await obs.stop_instance(9224, ctx)

            assert proc.poll() is not None
            assert 9224 not in obs.processes
            assert ctx.freed_obscura_ports == [9224]
        finally:
            if proc.poll() is None:
                proc.kill()
    asyncio.run(_run())


def test_obscura_stop_kills_child_processes_of_tracked_process():
    async def _run():
        obs = _make_obscura()
        script = (
            "import subprocess, sys, time\n"
            "c = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
            "print(c.pid, flush=True)\n"
            "time.sleep(120)\n"
        )
        parent = subprocess.Popen([sys.executable, "-c", script], stdout=subprocess.PIPE, text=True)
        child_pid = int(parent.stdout.readline().strip())
        try:
            obs.processes[9225] = parent
            await obs.stop_instance(9225)

            assert parent.poll() is not None
            assert _is_gone(child_pid)
        finally:
            parent.stdout.close()
            if parent.poll() is None:
                parent.kill()
            with suppress(psutil.NoSuchProcess):
                psutil.Process(child_pid).kill()
    asyncio.run(_run())


def test_obscura_stop_never_kills_unrelated_process_holding_the_port():
    async def _run():
        port = _free_port()
        listener_script = (
            "import socket, time\n"
            "s = socket.socket()\n"
            "s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n"
            f"s.bind(('127.0.0.1', {port}))\n"
            "s.listen()\n"
            "print('up', flush=True)\n"
            "time.sleep(120)\n"
        )
        unrelated = subprocess.Popen([sys.executable, "-c", listener_script], stdout=subprocess.PIPE, text=True)
        assert unrelated.stdout.readline().strip() == "up"
        try:
            assert Obscura.is_port_in_use(port)

            obs = _make_obscura()
            dead_tracked = MagicMock()
            dead_tracked.poll.return_value = 0
            dead_tracked.pid = 99999999
            obs.processes[port] = dead_tracked

            await obs.stop_instance(port, StormContext())

            assert unrelated.poll() is None
            assert Obscura.is_port_in_use(port)
        finally:
            unrelated.stdout.close()
            unrelated.kill()
    asyncio.run(_run())


def test_obscura_stop_of_untracked_port_is_a_noop_and_does_not_free_it():
    async def _run():
        obs = _make_obscura()
        ctx = StormContext()
        tracked = subprocess.Popen(SLEEPER)
        try:
            obs.processes[9300] = tracked

            await obs.stop_instance(9301, ctx)

            assert tracked.poll() is None
            assert 9300 in obs.processes
            assert ctx.freed_obscura_ports == []
        finally:
            tracked.kill()
    asyncio.run(_run())


def test_obscura_cdp_ready_checks_real_endpoint():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/json/version":
                body = json.dumps({"webSocketDebuggerUrl": "ws://127.0.0.1/devtools/browser/x"}).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()

        def log_message(self, *args):
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assert Obscura._cdp_ready(server.server_address[1]) is True
    finally:
        server.shutdown()
        server.server_close()

    class NotCdp(Handler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

    server = HTTPServer(("127.0.0.1", 0), NotCdp)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assert Obscura._cdp_ready(server.server_address[1]) is False
    finally:
        server.shutdown()
        server.server_close()

    assert Obscura._cdp_ready(_free_port()) is False


def test_obscura_spawn_instance_command_flags():
    obs = _make_obscura()
    obs.obscura_path = "/usr/bin/obscura"
    ctx = StormContext()
    ctx.obscura_current_port = 9222

    captured_cmd = []

    def mock_popen(cmd, *args, **kwargs):
        captured_cmd.extend(cmd)
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.pid = 9999
        return mock_proc

    async def _run():
        with patch("lib.core.Obscura.Popen", side_effect=mock_popen), \
             patch.object(obs, "_cdp_ready", return_value=True), \
             patch.object(obs, "is_port_in_use", side_effect=[False, True]):
            port = await obs.spawn_instance(ctx)
            assert port == 9222
            assert obs.processes[9222].pid == 9999
            assert captured_cmd[0] == "/usr/bin/obscura"
            assert "--v8-flags=--max-old-space-size=32" in captured_cmd
            assert "serve" in captured_cmd
            assert "--port" in captured_cmd
            assert "9222" in captured_cmd
            assert "--quiet" in captured_cmd
    asyncio.run(_run())


def test_obscura_spawn_popen_oserror_becomes_runtime_error():
    obs = _make_obscura()
    ctx = StormContext()

    async def _run():
        with patch("lib.core.Obscura.Popen", side_effect=FileNotFoundError("gone")), \
             patch.object(obs, "is_port_in_use", return_value=False):
            with pytest.raises(RuntimeError, match="Failed to launch Obscura"):
                await obs.spawn_instance(ctx)
        assert obs.processes == {}
    asyncio.run(_run())


def test_obscura_spawn_does_not_register_when_process_died_and_foreign_listener_holds_port():
    obs = _make_obscura()
    ctx = StormContext()
    cdp_probe = MagicMock(return_value=True)

    def mock_popen(cmd, *args, **kwargs):
        proc = MagicMock()
        proc.poll.side_effect = itertools.chain([None], itertools.repeat(1))
        proc.pid = 4242
        return proc

    async def _run():
        port_checks = iter([False] + [True] * 1000)
        with patch("lib.core.Obscura.Popen", side_effect=mock_popen), \
             patch.object(obs, "_cdp_ready", cdp_probe), \
             patch.object(obs, "is_port_in_use", side_effect=lambda p: next(port_checks)):
            with pytest.raises(RuntimeError):
                await obs.spawn_instance(ctx)
        assert obs.processes == {}
        cdp_probe.assert_not_called()
    asyncio.run(_run())


def test_obscura_spawn_requires_cdp_endpoint_not_just_open_port():
    obs = _make_obscura()
    ctx = StormContext()
    killed = []

    def mock_popen(cmd, *args, **kwargs):
        proc = MagicMock()
        proc.poll.return_value = None
        proc.pid = 5151
        return proc

    async def _run():
        port_checks = itertools.cycle([False] + [True] * 50)
        with patch("lib.core.Obscura.Popen", side_effect=mock_popen), \
             patch("lib.core.Obscura.asyncio.sleep", new=AsyncMock()), \
             patch.object(obs, "_cdp_ready", return_value=False), \
             patch.object(obs, "_terminate_process_tree", side_effect=lambda p, t=2: killed.append(p)), \
             patch.object(obs, "is_port_in_use", side_effect=lambda p: next(port_checks)):
            with pytest.raises(RuntimeError):
                await obs.spawn_instance(ctx)
        assert obs.processes == {}
        assert len(killed) == 20
    asyncio.run(_run())


def test_streamstorm_cleanup_calls_obscura_cleanup():
    async def _run():
        storm = _make_storm()
        try:
            assert storm.obscura is not None
            await storm.cleanup()
            storm.obscura.cleanup.assert_called_once()
        finally:
            StreamStorm.ss_instance = None

    asyncio.run(_run())


def test_streamstorm_uses_engine_captured_in_context_not_live_settings():
    storm = _make_storm(engine="chromium")
    try:
        assert storm.obscura is None
        assert storm.context.engine == "chromium"
    finally:
        StreamStorm.ss_instance = None


def test_assign_obscura_port_failure_shrinks_total_on_any_exception():
    async def _run():
        storm = _make_storm(channels=[1, 2])
        try:
            storm.obscura.spawn_instance = AsyncMock(side_effect=OSError("boom"))
            with patch("lib.core.StreamStorm.sio.emit", new=AsyncMock()) as emit:
                result = await storm._assign_obscura_port(0, 1, "a")
            assert result is None
            assert storm.context.total_instances == 1
            emit.assert_awaited_once()

            storm.obscura.spawn_instance = AsyncMock(return_value=9230)
            assert await storm._assign_obscura_port(1, 2, "b") == 9230
            assert storm.context.total_instances == 1

            storm.obscura = None
            assert await storm._assign_obscura_port(1, 2, "b") == 0
        finally:
            StreamStorm.ss_instance = None
    asyncio.run(_run())


def test_get_start_storm_wait_time_uses_fixed_total():
    storm = _make_storm(channels=[1, 2, 3, 4])
    try:
        storm.context.slow_mode = 8
        storm.context.total_instances = 1
        assert storm.get_start_storm_wait_time(2, 4) == 4.0
        assert storm.get_start_storm_wait_time(2) == 16.0
        storm.context.total_instances = 0
        assert storm.get_start_storm_wait_time(2) == 0.0
    finally:
        StreamStorm.ss_instance = None


@contextmanager
def _prepared_for_start(storm: StreamStorm, channels: dict[str, dict]):
    storm.environment_dir = "/tmp"
    storm.cookies = []
    storm.context.total_channels = 10
    storm.context.all_channels = channels
    with patch.object(StreamStorm, "check_channels_available", new=AsyncMock()), \
         patch.object(StreamStorm, "get_available_temp_profiles", new=MagicMock(return_value=[f"p{i}" for i in range(len(channels))])):
        yield


def test_start_with_every_obscura_spawn_failing_finishes_cleanly():
    async def _run():
        storm = _make_storm(channels=[1, 2])
        try:
            storm.obscura.spawn_instance = AsyncMock(side_effect=OSError("binary vanished"))
            real_sleep = asyncio.sleep

            async def fast_sleep(_):
                await real_sleep(0)

            with _prepared_for_start(storm, {"1": {"name": "a"}, "2": {"name": "b"}}), \
                 patch("lib.core.StreamStorm.sleep", new=fast_sleep), \
                 patch("lib.core.StreamStorm.sio.emit", new=AsyncMock()):
                await storm.start()
                worker = storm._background_tasks[0]
                await asyncio.wait_for(worker, timeout=5)

                assert storm.context.total_instances == 0
                assert storm.context.spawn_in_progress == 0
                assert storm.context.run_stopper_event.is_set()
                assert storm.obscura.spawn_instance.await_count == 2
                await storm.cleanup()
        finally:
            StreamStorm.ss_instance = None
    asyncio.run(_run())


def test_start_partial_spawn_failure_keeps_counts_and_wait_times_consistent():
    async def _run():
        storm = _make_storm(channels=[1, 2])
        try:
            storm.obscura.spawn_instance = AsyncMock(side_effect=[OSError("x"), 9223])
            real_sleep = asyncio.sleep

            async def fast_sleep(_):
                await real_sleep(0)

            created = []

            class FakeInstance:
                def __init__(self, index, profile_dir, wait_time, channel_name, cookies, context, port):
                    created.append((index, wait_time, port))

                async def start(self):
                    return None

            with _prepared_for_start(storm, {"1": {"name": "a"}, "2": {"name": "b"}}), \
                 patch("lib.core.StreamStorm.sleep", new=fast_sleep), \
                 patch("lib.core.StreamStorm.SeparateInstance", FakeInstance), \
                 patch("lib.core.StreamStorm.sio.emit", new=AsyncMock()):
                await storm.start()
                worker = storm._background_tasks[0]
                await asyncio.wait_for(worker, timeout=5)

                assert created == [(2, 2.5, 9223)]
                assert storm.context.total_instances == 1
                assert storm.context.spawn_in_progress == 0
                await storm.cleanup()
        finally:
            StreamStorm.ss_instance = None
    asyncio.run(_run())


def _make_separate_instance(context: StormContext, port: int = 9222):
    from lib.core.SeparateInstance import SeparateInstance

    instance = SeparateInstance(
        index=1,
        user_data_dir="C:\\test\\profile_1",
        wait_time=0,
        channel_name="Speed",
        cookies=[],
        storm_context=context,
        obscura_port=port
    )
    return instance


def test_separate_instance_cleanup_on_error_stops_obscura_and_sets_stopper():
    async def _run():
        from playwright.async_api import Error as PlaywrightError

        context = StormContext()
        context.total_instances = 3
        mock_obscura = MagicMock()
        mock_obscura.stop_instance = AsyncMock()
        context.obscura = mock_obscura

        instance = _make_separate_instance(context)

        with patch.object(instance, "login", side_effect=PlaywrightError("Target page, context or browser has been closed")), \
             patch.object(instance, "emit_instance_status", new=AsyncMock()), \
             patch.object(instance, "close_browser", new=AsyncMock()):

            await instance.start()

            mock_obscura.stop_instance.assert_called_once_with(9222, context)
            assert context.run_stopper_event.is_set()
            assert context.total_instances == 2
            assert instance.obscura_port == 0
            assert not instance._is_alive
            assert not await instance.is_instance_alive()

    asyncio.run(_run())


def test_separate_instance_failure_after_login_before_ready_shrinks_total_once():
    async def _run():
        from playwright.async_api import Error as PlaywrightError

        context = StormContext()
        context.total_instances = 3
        context.obscura = MagicMock(stop_instance=AsyncMock())

        instance = _make_separate_instance(context)
        instance.page = MagicMock(set_viewport_size=AsyncMock())

        with patch.object(instance, "login", new=AsyncMock(return_value=True)), \
             patch.object(instance, "go_to_page", new=AsyncMock(side_effect=PlaywrightError("nav failed"))), \
             patch.object(instance, "emit_instance_status", new=AsyncMock()), \
             patch.object(instance, "close_browser", new=AsyncMock()):

            await instance.start()

        assert context.total_instances == 2
        assert context.ready_to_storm_instances == 0
        context.obscura.stop_instance.assert_awaited_once_with(9222, context)

    asyncio.run(_run())


def test_separate_instance_ready_worker_does_not_shrink_total_on_exit():
    async def _run():
        from lib.utils.exceptions import ElementNotFound

        context = StormContext()
        context.total_instances = 3
        context.messages = ["hi"]
        context.ready_event.set()
        context.pause_event.set()
        context.obscura = MagicMock(stop_instance=AsyncMock())

        instance = _make_separate_instance(context)
        instance.page = MagicMock(set_viewport_size=AsyncMock())

        with patch.object(instance, "login", new=AsyncMock(return_value=True)), \
             patch.object(instance, "go_to_page", new=AsyncMock()), \
             patch.object(instance, "send_message", new=AsyncMock(side_effect=ElementNotFound("chat"))), \
             patch.object(instance, "emit_instance_status", new=AsyncMock()), \
             patch.object(instance, "close_browser", new=AsyncMock()):

            await instance.start()

        assert context.ready_to_storm_instances == 1
        assert context.total_instances == 3

    asyncio.run(_run())


def test_separate_instance_finally_is_exception_safe():
    async def _run():
        from playwright.async_api import Error as PlaywrightError

        context = StormContext()
        context.total_instances = 2
        context.obscura = MagicMock(stop_instance=AsyncMock())

        instance = _make_separate_instance(context)

        async def emit(index, status):
            if status == 0:
                raise KeyError("missing channel")

        close_browser = AsyncMock(side_effect=RuntimeError("close failed"))

        with patch.object(instance, "login", side_effect=PlaywrightError("closed")), \
             patch.object(instance, "emit_instance_status", new=emit), \
             patch.object(instance, "close_browser", new=close_browser):

            await instance.start()

        close_browser.assert_awaited_once()
        context.obscura.stop_instance.assert_awaited_once_with(9222, context)
        assert context.run_stopper_event.is_set()

    asyncio.run(_run())


def test_separate_instance_profile_dir_name_cross_platform():
    from lib.core.SeparateInstance import SeparateInstance

    context = StormContext()
    win_inst = SeparateInstance(
        index=1,
        user_data_dir="C:\\Users\\test\\Environment\\temp_profile_1",
        storm_context=context,
    )
    posix_inst = SeparateInstance(
        index=2,
        user_data_dir="/home/user/.local/share/StreamStorm/Environment/temp_profile_2",
        storm_context=context,
    )
    assert win_inst.profile_dir_name == "temp_profile_1"
    assert posix_inst.profile_dir_name == "temp_profile_2"


def test_separate_instance_inherits_engine_and_login_method_from_context():
    context = StormContext()
    context.engine = "chromium"
    context.login_method = "profiles"
    instance = _make_separate_instance(context)
    assert instance._engine == "chromium"
    assert instance._login_method == "profiles"


def _stopper_storm() -> StreamStorm:
    return _make_storm()


def test_storm_stopper_triggers_cleanup_when_all_instances_dead():
    async def _run():
        from lib.utils.StormStopper import background_storm_stopper
        from lib.core.EngineContext import EngineContext

        storm = _stopper_storm()
        with patch("lib.utils.StormStopper.sio.emit", new=AsyncMock()) as mock_sio_emit, \
             patch("lib.utils.StormStopper.sleep", new=AsyncMock()) as mock_sleep:

            EngineContext.set_busy("Testing")
            storm.context.run_stopper_event.set()

            call_count = 0
            async def fake_sleep(duration):
                nonlocal call_count
                call_count += 1
                if call_count > 1:
                    raise asyncio.CancelledError()

            mock_sleep.side_effect = fake_sleep

            try:
                await background_storm_stopper()
            except asyncio.CancelledError:
                pass

            storm.obscura.cleanup.assert_called_once()
            assert StreamStorm.ss_instance is None
            assert not EngineContext.is_busy()
            mock_sio_emit.assert_called_once_with('storm_stopped', room="streamstorm")

    asyncio.run(_run())


def test_storm_stopper_waits_while_spawn_in_progress():
    async def _run():
        from lib.utils.StormStopper import background_storm_stopper
        from lib.core.EngineContext import EngineContext

        storm = _stopper_storm()
        try:
            with patch("lib.utils.StormStopper.sio.emit", new=AsyncMock()) as mock_sio_emit, \
                 patch("lib.utils.StormStopper.sleep", new=AsyncMock()) as mock_sleep:

                EngineContext.set_busy("Testing")
                storm.context.run_stopper_event.set()
                storm.context.spawn_in_progress = 1

                call_count = 0
                async def fake_sleep(duration):
                    nonlocal call_count
                    call_count += 1
                    if call_count > 2:
                        raise asyncio.CancelledError()

                mock_sleep.side_effect = fake_sleep

                try:
                    await background_storm_stopper()
                except asyncio.CancelledError:
                    pass

                storm.obscura.cleanup.assert_not_called()
                assert StreamStorm.ss_instance is storm
                mock_sio_emit.assert_not_called()
        finally:
            StreamStorm.ss_instance = None
            EngineContext.reset()

    asyncio.run(_run())


def test_kill_instance_zeroes_port_before_stop_and_decrements_once():
    async def _run():
        from lib.api.routers.StormRouter import kill_instance
        from lib.api.validation import KillInstanceData

        storm = _make_storm()
        try:
            instance = MagicMock()
            instance.index = 1
            instance.obscura_port = 9222
            instance.ready_counted = False
            instance.profile_dir_name = "p1"
            instance.close_browser = AsyncMock()

            seen_ports = []

            async def stop(port, ctx):
                seen_ports.append((port, instance.obscura_port))

            storm.obscura.stop_instance = stop
            storm.context.total_instances = 3
            storm.context.each_channel_instances.append(instance)

            with patch("lib.api.routers.StormRouter.sio.emit", new=AsyncMock()):
                response = await kill_instance(KillInstanceData(index=1, name="x"))

            assert response.status_code == 200
            assert seen_ports == [(9222, 0)]
            assert storm.context.total_instances == 3
            assert instance not in storm.context.each_channel_instances

            ready_instance = MagicMock()
            ready_instance.index = 2
            ready_instance.obscura_port = 0
            ready_instance.ready_counted = True
            ready_instance.profile_dir_name = "p2"
            ready_instance.close_browser = AsyncMock()
            storm.context.each_channel_instances.append(ready_instance)

            with patch("lib.api.routers.StormRouter.sio.emit", new=AsyncMock()):
                await kill_instance(KillInstanceData(index=2, name="y"))

            assert storm.context.total_instances == 2
        finally:
            StreamStorm.ss_instance = None

    asyncio.run(_run())


def test_lifespan_shutdown_kills_obscura_off_the_event_loop():
    async def _run():
        from fastapi import FastAPI
        from lib.api.lib import LifeSpan

        main_thread = threading.get_ident()
        seen = []

        async def noop():
            return None

        with patch.object(LifeSpan, "background_storm_stopper", noop), \
             patch.object(LifeSpan, "emit_system_metrics", noop), \
             patch.object(LifeSpan.Obscura, "kill_all", side_effect=lambda: seen.append(threading.get_ident())):
            async with LifeSpan.lifespan(FastAPI()):
                pass

        assert len(seen) == 1
        assert seen[0] != main_thread

    asyncio.run(_run())


def test_obscura_hydration_and_channel_switch_on_click():
    async def _run():
        from lib.core.Playwright import Playwright

        pw = Playwright(user_data_dir="/tmp/test", background=True, index=2, channel_name="Speed")
        pw._is_obscura = True
        pw.page = MagicMock()
        pw.page.goto = AsyncMock()
        pw.page.evaluate = AsyncMock(return_value={"hydrated": True, "page": "account"})

        mock_locator = MagicMock()
        mock_locator.wait_for = AsyncMock()
        mock_locator.get_attribute = AsyncMock(side_effect=["/signin?action_handle_signin=true&pageid=123", "false"])
        mock_locator.click = AsyncMock()
        pw.page.locator = MagicMock(return_value=mock_locator)

        await pw.find_and_click_element(
            "//*[@id='contents']/ytd-account-item-renderer[.//text()[normalize-space(.)='Speed']]",
            "channel_element",
        )

        mock_locator.click.assert_called_once()
        pw.page.goto.assert_called_once_with("https://www.youtube.com/signin?action_handle_signin=true&pageid=123")
        pw.page.evaluate.assert_called_once()

    asyncio.run(_run())


def _wire_playwright_mocks(pw, mock_pw_driver):
    mock_browser = AsyncMock()
    mock_browser.on = MagicMock()
    mock_context = AsyncMock()
    mock_context.on = MagicMock()
    mock_context.browser = mock_browser
    mock_page = AsyncMock()
    mock_page.on = MagicMock()
    mock_page.set_default_navigation_timeout = MagicMock()
    mock_page.set_default_timeout = MagicMock()
    mock_pw_driver.chromium.connect_over_cdp = AsyncMock(return_value=mock_browser)
    mock_pw_driver.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page


def test_playwright_uses_constructor_engine_not_live_settings():
    async def _run():
        from lib.core.Playwright import Playwright

        mock_pw_driver = AsyncMock()
        Playwright._shared_playwright = None
        Playwright._shared_playwright_refcount = 0

        with patch("lib.core.Playwright.async_playwright") as mock_apw, \
             patch("lib.core.Playwright.settings") as live_settings:
            live_settings.engine = "obscura"
            live_settings.login_method = "cookies"
            mock_starter = MagicMock()
            mock_starter.start = AsyncMock(return_value=mock_pw_driver)
            mock_apw.return_value = mock_starter

            chromium_pw = Playwright(user_data_dir="/tmp/p1", background=True, index=1, channel_name="Ch1",
                                     login_method="cookies", engine="chromium")
            obscura_pw = Playwright(user_data_dir="/tmp/p2", background=True, index=2, channel_name="Ch2",
                                    login_method="cookies", engine="obscura")

            for pw in (chromium_pw, obscura_pw):
                _wire_playwright_mocks(pw, mock_pw_driver)

            with patch.object(Playwright, "_Playwright__get_browser_version", AsyncMock(return_value="131.0")):
                live_settings.engine = "chromium"
                await chromium_pw.open_browser(obscura_port=9222)
                live_settings.engine = "obscura"
                await obscura_pw.open_browser(obscura_port=9223)

            assert chromium_pw._is_obscura is False
            assert obscura_pw._is_obscura is True

            await chromium_pw.close_browser("done")
            await obscura_pw.close_browser("done")

        Playwright._shared_playwright = None
        Playwright._shared_playwright_refcount = 0

    asyncio.run(_run())


def test_shared_playwright_refcounting():
    async def _run():
        from lib.core.Playwright import Playwright

        mock_pw_driver = AsyncMock()
        mock_pw_driver.stop = AsyncMock()

        Playwright._shared_playwright = None
        Playwright._shared_playwright_refcount = 0

        with patch("lib.core.Playwright.async_playwright") as mock_apw:
            mock_starter = MagicMock()
            mock_starter.start = AsyncMock(return_value=mock_pw_driver)
            mock_apw.return_value = mock_starter

            pw1 = Playwright(user_data_dir="/tmp/p1", background=True, index=1, channel_name="Ch1")
            pw2 = Playwright(user_data_dir="/tmp/p2", background=True, index=2, channel_name="Ch2")

            with patch.object(pw1, "_Playwright__get_chromium_options", AsyncMock(return_value={"args": [], "viewport": {}})), \
                 patch.object(pw2, "_Playwright__get_chromium_options", AsyncMock(return_value={"args": [], "viewport": {}})), \
                 patch.object(pw1, "_Playwright__get_browser_version", AsyncMock(return_value="131.0")), \
                 patch.object(pw2, "_Playwright__get_browser_version", AsyncMock(return_value="131.0")):

                mock_pw_driver.chromium.connect_over_cdp = AsyncMock()
                mock_browser = AsyncMock()
                mock_browser.on = MagicMock()
                mock_context = AsyncMock()
                mock_context.on = MagicMock()
                mock_context.browser = mock_browser
                mock_page = AsyncMock()
                mock_page.on = MagicMock()
                mock_page.set_default_navigation_timeout = MagicMock()
                mock_page.set_default_timeout = MagicMock()
                mock_pw_driver.chromium.connect_over_cdp.return_value = mock_browser
                mock_browser.new_context.return_value = mock_context
                mock_context.new_page.return_value = mock_page

                await pw1.open_browser(obscura_port=9222)
                assert Playwright._shared_playwright_refcount == 1
                assert pw1.playwright is mock_pw_driver

                await pw2.open_browser(obscura_port=9223)
                assert Playwright._shared_playwright_refcount == 2
                assert pw2.playwright is mock_pw_driver
                mock_starter.start.assert_called_once()

                await pw1.close_browser("Instance 1 closed")
                assert Playwright._shared_playwright_refcount == 1
                assert Playwright._shared_playwright is mock_pw_driver
                mock_pw_driver.stop.assert_not_called()

                await pw2.close_browser("Instance 2 closed")
                assert Playwright._shared_playwright_refcount == 0
                assert Playwright._shared_playwright is None
                mock_pw_driver.stop.assert_called_once()

    asyncio.run(_run())
