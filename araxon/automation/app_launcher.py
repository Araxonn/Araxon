import os
import subprocess
import asyncio
import psutil
from araxon.core.config import settings
from araxon.core.logger import logger


class AppLauncher:
    """
    Launches desktop applications on Windows using
    multiple strategies: shell:AppsFolder for Store apps,
    direct exe paths, and PowerShell Start-Process.
    """

    # Apps that need exe path directly (not Store apps)
    EXE_PATH_APPS = {
        "utorrent": f"C:\\Users\\{os.getenv('USERNAME', 'lucky')}\\AppData\\Roaming\\utorrent\\uTorrent.exe",
        "ollama": f"C:\\Users\\{os.getenv('USERNAME', 'lucky')}\\AppData\\Local\\Programs\\Ollama\\ollama app.exe",
        "vlc": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
        "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
    }

    # Apps that use simple shell commands
    SHELL_COMMAND_APPS = {
        "chrome": "chrome",
        "google chrome": "chrome",
        "edge": "msedge",
        "microsoft edge": "msedge",
        "notepad": "notepad",
        "calculator": "calc",
        "task manager": "taskmgr",
        "control panel": "control",
        "file explorer": "explorer",
        "explorer": "explorer",
        "cmd": "cmd",
        "command prompt": "cmd",
        "regedit": "regedit",
        "paint": "mspaint",
    }

    # VS Code special handling
    VSCODE_APPS = {
        "vs code", "vscode", "visual studio code",
        "code", "cursor"
    }

    def __init__(self):
        """Initialize AppLauncher with app map from settings."""
        self.app_map = settings.APP_MAP
        logger.info("AppLauncher initialized with "
                    f"{len(self.app_map)} apps.")

    def _find_app_key(self, app_name: str) -> tuple[str, str] | None:
        """
        Find matching app key and AppID from APP_MAP.
        Returns (key, app_id) or None.
        """
        normalized = app_name.lower().strip()
        for key, app_id in self.app_map.items():
            if key in normalized or normalized in key:
                return key, app_id
        return None

    async def launch(self, app_name: str) -> str:
        """
        Launch an application using the best available strategy.
        Tries multiple methods in order until one succeeds.
        """
        normalized = app_name.lower().strip()
        logger.info(f"[APP] Launch request: '{app_name}'")

        # Strategy 1: VS Code / Cursor special handling
        for vscode_key in self.VSCODE_APPS:
            if vscode_key in normalized:
                return await self._launch_vscode(normalized)

        # Strategy 2: Direct exe path apps
        for key, path in self.EXE_PATH_APPS.items():
            if key in normalized:
                return await self._launch_exe(path, app_name)

        # Strategy 3: Simple shell command apps
        for key, cmd in self.SHELL_COMMAND_APPS.items():
            if key in normalized:
                return await self._launch_shell_cmd(cmd, app_name)

        # Strategy 4: Store apps via shell:AppsFolder
        match = self._find_app_key(normalized)
        if match:
            key, app_id = match
            # Check if it looks like a Store AppID
            if ("_8wekyb3d8bbwe" in app_id or
                    "com.squirrel" in app_id or
                    "AB." in app_id or
                    "!" in app_id):
                return await self._launch_store_app(
                    app_id, app_name
                )
            # Otherwise try as shell command
            return await self._launch_shell_cmd(app_id, app_name)

        # Strategy 5: PowerShell Start-Process fallback
        return await self._launch_powershell(normalized, app_name)

    async def _launch_vscode(self, normalized: str) -> str:
        """Launch VS Code or Cursor using their CLI commands."""
        cmd = "cursor" if "cursor" in normalized else "code"
        try:
            subprocess.Popen(
                f'start /b {cmd} .',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            logger.info(f"[APP] Launched {cmd} successfully.")
            return f"Opened {cmd}"
        except Exception as e:
            # Fallback: use PowerShell
            try:
                subprocess.Popen(
                    ["powershell", "-Command",
                     f'Start-Process "{cmd}"'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return f"Opened {cmd}"
            except Exception as e2:
                logger.error(f"[APP] VS Code launch failed: {e2}")
                return f"Could not open {cmd}"

    async def _launch_exe(self, path: str, app_name: str) -> str:
        """Launch app directly from exe path."""
        if not os.path.exists(path):
            logger.warning(f"[APP] Exe not found: {path}")
            return await self._launch_powershell(
                app_name.lower(), app_name
            )
        try:
            subprocess.Popen(
                [path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info(f"[APP] Launched via exe: {path}")
            return f"Opened {app_name}"
        except Exception as e:
            logger.error(f"[APP] Exe launch failed: {e}")
            return f"Could not open {app_name}"

    async def _launch_shell_cmd(
        self, cmd: str, app_name: str
    ) -> str:
        """Launch app using shell start command."""
        try:
            subprocess.Popen(
                f'start {cmd}',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info(f"[APP] Launched via shell: {cmd}")
            return f"Opened {app_name}"
        except Exception as e:
            logger.error(f"[APP] Shell launch failed: {e}")
            return f"Could not open {app_name}"

    async def _launch_store_app(
        self, app_id: str, app_name: str
    ) -> str:
        """
        Launch Microsoft Store app using shell:AppsFolder.
        This is the correct method for all Store apps
        including Spotify, WhatsApp, Teams etc.
        """
        shell_path = f"shell:AppsFolder\\{app_id}"
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 f'Start-Process "{shell_path}"'],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(
                    f"[APP] Launched Store app: {app_name} "
                    f"AppID: {app_id}"
                )
                return f"Opened {app_name}"
            else:
                err = result.stderr.decode().strip()
                logger.warning(
                    f"[APP] Store launch returned "
                    f"code {result.returncode}: {err}"
                )
                # Try explorer shell as fallback
                return await self._launch_explorer_shell(
                    app_id, app_name
                )
        except subprocess.TimeoutExpired:
            logger.warning(f"[APP] Store launch timed out: {app_name}")
            return f"Opened {app_name}"
        except Exception as e:
            logger.error(f"[APP] Store launch error: {e}")
            return await self._launch_explorer_shell(
                app_id, app_name
            )

    async def _launch_explorer_shell(
        self, app_id: str, app_name: str
    ) -> str:
        """Fallback: open via explorer shell:AppsFolder."""
        try:
            shell_path = f"shell:AppsFolder\\{app_id}"
            subprocess.Popen(
                ["explorer", shell_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info(
                f"[APP] Launched via explorer shell: {app_name}"
            )
            return f"Opened {app_name}"
        except Exception as e:
            logger.error(f"[APP] Explorer shell failed: {e}")
            return f"Could not open {app_name}"

    async def _launch_powershell(
        self, cmd: str, app_name: str
    ) -> str:
        """Last resort: PowerShell Start-Process."""
        try:
            subprocess.Popen(
                ["powershell", "-Command",
                 f'Start-Process "{cmd}"'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info(
                f"[APP] Launched via PowerShell: {app_name}"
            )
            return f"Opened {app_name}"
        except Exception as e:
            logger.error(
                f"[APP] All strategies failed for {app_name}: {e}"
            )
            return (f"Could not open {app_name}. "
                    f"Try opening it manually.")

    async def close(self, app_name: str) -> str:
        """Close a running application by process name."""
        normalized = app_name.lower().strip()
        process_names = {
            "spotify": ["Spotify.exe"],
            "chrome": ["chrome.exe"],
            "discord": ["Discord.exe"],
            "vs code": ["Code.exe"],
            "vscode": ["Code.exe"],
            "cursor": ["Cursor.exe"],
            "teams": ["Teams.exe", "ms-teams.exe"],
            "telegram": ["Telegram.exe"],
            "whatsapp": ["WhatsApp.exe"],
            "notepad": ["Notepad.exe", "notepad.exe"],
            "vlc": ["vlc.exe"],
            "postman": ["Postman.exe"],
            "bluestacks": ["HD-Player.exe"],
        }

        procs_to_kill = []
        for key, proc_names in process_names.items():
            if key in normalized:
                procs_to_kill = proc_names
                break

        if not procs_to_kill:
            procs_to_kill = [f"{normalized}.exe"]

        killed = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] in procs_to_kill:
                    proc.kill()
                    killed.append(proc.info['name'])
            except (psutil.NoSuchProcess,
                    psutil.AccessDenied):
                pass

        if killed:
            logger.info(f"[APP] Closed: {', '.join(killed)}")
            return f"Closed {app_name}"
        return f"{app_name} was not running"

    async def is_running(self, app_name: str) -> bool:
        """Check if an app process is currently running."""
        normalized = app_name.lower().strip()
        check_names = {
            "spotify": ["Spotify.exe"],
            "chrome": ["chrome.exe"],
            "discord": ["Discord.exe"],
            "vs code": ["Code.exe"],
            "cursor": ["Cursor.exe"],
            "teams": ["Teams.exe"],
            "telegram": ["Telegram.exe"],
            "whatsapp": ["WhatsApp.exe"],
        }
        proc_names = check_names.get(normalized,
                                     [f"{normalized}.exe"])
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in proc_names:
                    return True
            except (psutil.NoSuchProcess,
                    psutil.AccessDenied):
                pass
        return False

    def get_available_apps(self) -> list[str]:
        """Return list of all launchable app names."""
        return list(self.app_map.keys())
