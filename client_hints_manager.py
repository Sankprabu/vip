# client_hints_manager.py

from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineUrlRequestInterceptor
from PyQt6.QtCore import QObject
import random

class ClientHintsInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, client_hints_manager):
        super().__init__()
        self.manager = client_hints_manager

    def interceptRequest(self, info):
        if self.manager.is_active:
            headers = self.manager.get_current_headers()
            for header, value in headers.items():
                info.setHttpHeader(header.encode(), value.encode())

class ClientHintsManager(QObject):
    def __init__(self):
        super().__init__()
        self.is_active = False
        self.mode = "default"
        self.interceptor = ClientHintsInterceptor(self)

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def set_mode(self, mode):
        if mode in ["default", "hide", "manipulate", "randomize"]:
            self.mode = mode
        else:
            raise ValueError("Mode tidak valid. Pilih 'default', 'hide', 'manipulate', atau 'randomize'.")

    def apply_to_profile(self, profile: QWebEngineProfile):
        profile.setUrlRequestInterceptor(self.interceptor)

    def get_current_headers(self):
        if not self.is_active:
            return {}

        if self.mode == "default":
            return self._get_default_hints()
        elif self.mode == "hide":
            return {}
        elif self.mode == "manipulate":
            return self._get_manipulated_hints()
        elif self.mode == "randomize":
            return self._get_random_hints()
        return {}

    def _get_default_hints(self):
        return {
            'Sec-CH-UA': '"Chromium";v="96", "Google Chrome";v="96"',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Full-Version': '"96.0.4664.45"',
            'Sec-CH-UA-Platform-Version': '"10.0.0"',
            'Sec-CH-UA-Arch': '"x86"',
            'Sec-CH-UA-Bitness': '"64"',
            'Sec-CH-UA-Model': '""',
            'Sec-CH-UA-Form-Factors': '"Desktop"',
            'Sec-CH-Lang': '"en-US"',
            'Sec-CH-Width': '1920'
        }

    def _get_manipulated_hints(self):
        return {
            'Sec-CH-UA': '"Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'Sec-CH-UA-Platform': '"Linux"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Full-Version': '"96.0.4664.45"',
            'Sec-CH-UA-Platform-Version': '"5.4.0"',
            'Sec-CH-UA-Arch': '"x86"',
            'Sec-CH-UA-Bitness': '"64"',
            'Sec-CH-UA-Model': '""',
            'Sec-CH-UA-Form-Factors': '"Desktop"',
            'Sec-CH-Lang': '"en-US"',
            'Sec-CH-Width': '1920'
        }

    def _get_random_hints(self):
        platforms = ['Windows', 'MacOS', 'Linux']
        browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
        versions = ['90', '91', '92', '93', '94', '95', '96']
        
        return {
            'Sec-CH-UA': f'"{random.choice(browsers)}";v="{random.choice(versions)}"',
            'Sec-CH-UA-Platform': f'"{random.choice(platforms)}"',
            'Sec-CH-UA-Mobile': '?0' if random.choice([True, False]) else '?1',
            'Sec-CH-UA-Full-Version': f'"{random.choice(versions)}.0.{random.randint(1000, 9999)}.{random.randint(10, 99)}"',
            'Sec-CH-UA-Platform-Version': f'"{random.randint(8, 11)}.{random.randint(0, 9)}.0"',
            'Sec-CH-UA-Arch': '"x86"' if random.choice([True, False]) else '"arm"',
            'Sec-CH-UA-Bitness': '"64"' if random.choice([True, False]) else '"32"',
            'Sec-CH-UA-Model': '""',
            'Sec-CH-UA-Form-Factors': '"Desktop"' if random.choice([True, False]) else '"Tablet"',
            'Sec-CH-Lang': f'"{random.choice(["en-US", "en-GB", "fr-FR", "de-DE", "es-ES"])}"',
            'Sec-CH-Width': str(random.choice([1366, 1440, 1920, 2560]))
        }