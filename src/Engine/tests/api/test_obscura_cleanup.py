import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from lib.core.Obscura import Obscura
from lib.core.StreamStorm import StreamStorm
from lib.api.validation import StormData
from lib.core.StormContext import StormContext


def test_obscura_processes_dict_initialized():
    with patch("lib.core.Obscura.which", return_value="C:\\dummy\\obscura.exe"):
        obs = Obscura()
        assert hasattr(obs, "processes")
        assert isinstance(obs.processes, dict)
        assert len(obs.processes) == 0


def test_obscura_binary_resolution_fallback_cross_platform():
    with patch("lib.core.Obscura.which", return_value=None), \
         patch("lib.core.Obscura.os_name", "posix"), \
         patch("lib.core.Obscura.Path.is_file", return_value=True):
        binary = Obscura._resolve_obscura_binary()
        assert binary is not None
        assert "obscura" in binary


def test_obscura_cleanup_terminates_all_processes():
    with patch("lib.core.Obscura.which", return_value="C:\\dummy\\obscura.exe"):
        obs = Obscura()
        mock_proc1 = MagicMock()
        mock_proc1.poll.return_value = None
        mock_proc1.pid = 1001

        mock_proc2 = MagicMock()
        mock_proc2.poll.return_value = None
        mock_proc2.pid = 1002

        obs.processes[9222] = mock_proc1
        obs.processes[9223] = mock_proc2

        obs.cleanup()

        mock_proc1.terminate.assert_called_once()
        mock_proc2.terminate.assert_called_once()
        assert len(obs.processes) == 0


def test_obscura_stop_single_instance():
    with patch("lib.core.Obscura.which", return_value="C:\\dummy\\obscura.exe"):
        obs = Obscura()
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.pid = 1003

        obs.processes[9224] = mock_proc
        obs.stop_instance(9224)

        mock_proc.terminate.assert_called_once()
        assert 9224 not in obs.processes


def test_streamstorm_cleanup_calls_obscura_cleanup():
    async def _run():
        storm_data = StormData(
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            chat_url="https://www.youtube.com/live_chat?v=dQw4w9WgXcQ",
            messages=["hello"],
            subscribe=False,
            subscribe_and_wait=False,
            subscribe_and_wait_time=0,
            slow_mode=5,
            channels=[1],
            background=False
        )

        with patch.object(StreamStorm, "load_cookies", return_value={}), \
             patch("lib.core.StreamStorm.Profiles.__init__", return_value=None), \
             patch("lib.core.StreamStorm.settings") as mock_settings:

            mock_settings.browser_engine = "obscura"
            mock_settings.login_method = "cookies"

            with patch("lib.core.StreamStorm.Obscura") as MockObscuraCls:
                mock_obscura_inst = MagicMock()
                MockObscuraCls.return_value = mock_obscura_inst

                storm = StreamStorm(storm_data)
                assert storm.obscura is mock_obscura_inst

                await storm.cleanup()

                mock_obscura_inst.cleanup.assert_called_once()

    asyncio.run(_run())


def test_separate_instance_cleanup_on_error_stops_obscura_and_sets_stopper():
    async def _run():
        from lib.core.SeparateInstance import SeparateInstance
        from playwright.async_api import Error as PlaywrightError

        context = StormContext()
        mock_obscura = MagicMock()
        context.obscura = mock_obscura

        instance = SeparateInstance(
            index=1,
            user_data_dir="C:\\test\\profile_1",
            wait_time=1.0,
            channel_name="Speed",
            cookies=[],
            storm_context=context,
            obscura_port=9222
        )

        with patch.object(instance, "login", side_effect=PlaywrightError("Target page, context or browser has been closed")), \
             patch.object(instance, "emit_instance_status", new=AsyncMock()), \
             patch.object(instance, "close_browser", new=AsyncMock()):

            await instance.start()

            # Verify Obscura instance for this port was stopped
            mock_obscura.stop_instance.assert_called_once_with(9222, context)
            # Verify run_stopper_event was set so StormStopper can clean up
            assert context.run_stopper_event.is_set()
            # Verify instance is marked dead
            assert not instance._is_alive
            assert not await instance.is_instance_alive()

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


def test_storm_stopper_triggers_cleanup_when_all_instances_dead():
    async def _run():
        from lib.utils.StormStopper import background_storm_stopper
        from lib.core.EngineContext import EngineContext

        storm_data = StormData(
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            chat_url="https://www.youtube.com/live_chat?v=dQw4w9WgXcQ",
            messages=["hello"],
            subscribe=False,
            subscribe_and_wait=False,
            subscribe_and_wait_time=0,
            slow_mode=5,
            channels=[1],
            background=False
        )

        with patch.object(StreamStorm, "load_cookies", return_value={}), \
             patch("lib.core.StreamStorm.Profiles.__init__", return_value=None), \
             patch("lib.core.StreamStorm.settings") as mock_settings, \
             patch("lib.utils.StormStopper.sio.emit", new=AsyncMock()) as mock_sio_emit, \
             patch("lib.utils.StormStopper.sleep", new=AsyncMock()) as mock_sleep:

            mock_settings.browser_engine = "obscura"
            mock_settings.login_method = "cookies"

            with patch("lib.core.StreamStorm.Obscura") as MockObscuraCls:
                mock_obscura = MagicMock()
                MockObscuraCls.return_value = mock_obscura

                storm = StreamStorm(storm_data)
                EngineContext.set_busy("Testing")
                storm.context.run_stopper_event.set()

                # Simulate background_storm_stopper running one check cycle
                # by making sleep raise CancelledError after first run
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

                # StreamStorm.cleanup() should have been called, cleaning up obscura
                mock_obscura.cleanup.assert_called_once()
                assert StreamStorm.ss_instance is None
                assert not EngineContext.is_busy()
                mock_sio_emit.assert_called_once_with('storm_stopped', room="streamstorm")

    asyncio.run(_run())


def test_capture_screenshot_invokes_screenshot():
    async def _run():
        from lib.core.Playwright import Playwright

        pw = Playwright(user_data_dir="C:\\test", background=False, index=1, channel_name="Speed")
        pw.page = MagicMock()
        pw.page.screenshot = AsyncMock()

        await pw.capture_screenshot("test_name")
        pw.page.screenshot.assert_called_once()

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


def test_shared_playwright_refcounting():
    async def _run():
        from lib.core.Playwright import Playwright

        mock_pw_driver = AsyncMock()
        mock_pw_driver.stop = AsyncMock()

        # Reset state before test
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
                mock_context = AsyncMock()
                mock_page = AsyncMock()
                mock_pw_driver.chromium.connect_over_cdp.return_value = mock_browser
                mock_browser.new_context.return_value = mock_context
                mock_context.new_page.return_value = mock_page

                await pw1.open_browser(obscura_port=9222)
                assert Playwright._shared_playwright_refcount == 1
                assert pw1.playwright is mock_pw_driver

                await pw2.open_browser(obscura_port=9223)
                assert Playwright._shared_playwright_refcount == 2
                assert pw2.playwright is mock_pw_driver
                mock_starter.start.assert_called_once()  # Shared! Only started once

                # Close first instance
                await pw1.close_browser("Instance 1 closed")
                assert Playwright._shared_playwright_refcount == 1
                assert Playwright._shared_playwright is mock_pw_driver
                mock_pw_driver.stop.assert_not_called()  # Still active for pw2

                # Close second instance
                await pw2.close_browser("Instance 2 closed")
                assert Playwright._shared_playwright_refcount == 0
                assert Playwright._shared_playwright is None
                mock_pw_driver.stop.assert_called_once()  # Stopped when last instance closed

    asyncio.run(_run())


def test_obscura_spawn_instance_command_flags():
    from lib.core.Obscura import Obscura
    from lib.core.StormContext import StormContext

    obs = Obscura()
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

    with patch("lib.core.Obscura.Popen", side_effect=mock_popen), \
         patch.object(obs, "is_port_in_use", side_effect=[False, True]):
        port = obs.spawn_instance(ctx)
        assert port == 9222
        assert captured_cmd[0] == "/usr/bin/obscura"
        assert "--v8-flags=--max-old-space-size=32" in captured_cmd
        assert "serve" in captured_cmd
        assert "--port" in captured_cmd
        assert "9222" in captured_cmd
        assert "--quiet" in captured_cmd

