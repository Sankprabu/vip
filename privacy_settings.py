from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtNetwork import QNetworkRequest

class PrivacySettings:
    def __init__(self, profile):
        self.profile = profile
        self.private_browsing_enabled = False
        self.dnt_enabled = False
        self.gpc_enabled = False
        # Inisialisasi custom headers dengan nilai default
        self.custom_headers = {
            "DNT": "0",
            "Sec-GPC": "0"
        }

    def set_dnt_enabled(self, enabled):
        self.dnt_enabled = enabled
        self.custom_headers["DNT"] = "1" if enabled else "0"
        self._update_privacy_script()

    def set_gpc_enabled(self, enabled):
        self.gpc_enabled = enabled
        self.custom_headers["Sec-GPC"] = "1" if enabled else "0"
        self._update_privacy_script()

    def _update_privacy_script(self):
        script = f"""
        Object.defineProperty(navigator, 'doNotTrack', {{
            get: function() {{ return "{('1' if self.dnt_enabled else '0')}"; }}
        }});
        Object.defineProperty(navigator, 'globalPrivacyControl', {{
            get: function() {{ return {str(self.gpc_enabled).lower()}; }}
        }});
    """
        if hasattr(self, 'current_page'):
            self.current_page.runJavaScript(script)

    def enable_private_browsing(self):
        self.private_browsing_enabled = True
        self.profile.setHttpUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15")
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        self.set_dnt_enabled(True)
        self.set_gpc_enabled(True)
        self.profile.downloadRequested.connect(self.add_headers_to_request)

    def disable_private_browsing(self):
        self.private_browsing_enabled = False
        self.profile.setHttpUserAgent("Custom Browser")
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        self.set_dnt_enabled(False)
        self.set_gpc_enabled(False)

    def add_headers_to_request(self, request):
        for header, value in self.custom_headers.items():
            request.setRawHeader(header.encode(), value.encode())

    def apply_to_page(self, page):
        self.current_page = page
        settings = page.settings()
        
        if self.private_browsing_enabled:
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, False)
        else:
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        
        self._update_privacy_script()

    def is_dnt_enabled(self):
        return self.dnt_enabled

    def is_gpc_enabled(self):
        return self.gpc_enabled