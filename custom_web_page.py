from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor
from PyQt6.QtCore import QUrl, pyqtSignal
import logging
import weakref
from functools import lru_cache
from jquery_manager import JQueryManager

class CustomWebPage(QWebEnginePage):
    consoleMessageReceived = pyqtSignal(str, int, str)

    def __init__(self, profile, ad_block_interceptor, privacy_settings, incognito_mode, 
                 safe_browsing, user_agent, parent=None):
        """Inisialisasi CustomWebPage dengan berbagai komponen"""
        super().__init__(profile, parent)
        
        # Gunakan weakref untuk mencegah circular references
        self.ad_block_interceptor = weakref.ref(ad_block_interceptor) if ad_block_interceptor else None
        self.privacy_settings = weakref.ref(privacy_settings) if privacy_settings else None
        self.incognito_mode = weakref.ref(incognito_mode) if incognito_mode else None
        self.safe_browsing = weakref.ref(safe_browsing) if safe_browsing else None
        self.user_agent = weakref.ref(user_agent) if user_agent else None
        
        # Setup logger dan jQuery manager
        self.logger = logging.getLogger('VipBrowser.CustomWebPage')
        self.jquery_manager = JQueryManager(profile)

        # Koneksi signal
        self.loadFinished.connect(self.on_load_finished)
        self.consoleMessageReceived.connect(self.handle_javascript_console_message)

        # Inisialisasi dan terapkan pengaturan
        self.initialize()
        self.apply_settings()

    def initialize(self):
        """Inisialisasi pengaturan dasar dan keamanan"""
        settings = self.settings()
        
        # Pengaturan keamanan dan fitur dasar
        settings_attributes = {
            QWebEngineSettings.WebAttribute.JavascriptEnabled: True,
            QWebEngineSettings.WebAttribute.LocalStorageEnabled: True,
            QWebEngineSettings.WebAttribute.WebGLEnabled: True,
            QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled: True,
            QWebEngineSettings.WebAttribute.ErrorPageEnabled: True,
            QWebEngineSettings.WebAttribute.PluginsEnabled: False,
            QWebEngineSettings.WebAttribute.FullScreenSupportEnabled: True,
            QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows: True,
            QWebEngineSettings.WebAttribute.AllowGeolocationOnInsecureOrigins: False,
        }
        
        for attribute, value in settings_attributes.items():
            settings.setAttribute(attribute, value)

    def on_load_finished(self, ok):
        """Handler untuk signal loadFinished"""
        if ok:
            self.logger.info("Halaman berhasil dimuat")
            self.jquery_manager.suntik_jquery_dengan_percobaan(self)
            self.execute_post_load_scripts()
        else:
            self.logger.error("Halaman gagal dimuat")

    def execute_post_load_scripts(self):
        """Eksekusi script setelah halaman dimuat"""
        self.jquery_manager.jalankan_jquery(self, """
            console.log('jQuery siap digunakan');
            console.log('Jumlah elemen pada halaman:', $('*').length);
        """)

    def javaScriptConsoleMessage(self, level, message, line, source_id):
        """Override metode untuk menangani pesan konsol JavaScript"""
        level_str = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR"
        }.get(level, "UNKNOWN")
        
        formatted_message = f"JavaScript {level_str}: {message} (line {line}) at {source_id}"
        self.consoleMessageReceived.emit(formatted_message, level, source_id)
        
        if self.jquery_manager:
            self.jquery_manager.tangani_konsol_javascript(level, message, line, source_id)

    def handle_javascript_console_message(self, message, level, source_id):
        """Handler untuk pesan konsol JavaScript"""
        self.logger.debug(message)

    def apply_settings(self):
        """Terapkan pengaturan browser"""
        try:
            if self.incognito_mode and self.incognito_mode().is_active():
                self.setup_incognito_mode()

            self.setup_interceptors()
            self.apply_privacy_settings()
            self.set_user_agent()

        except Exception as e:
            self.logger.error(f"Error applying settings: {str(e)}")

    def setup_incognito_mode(self):
        """Setup mode incognito"""
        incognito_profile = QWebEngineProfile()
        incognito_profile.setOffTheRecord(True)
        self.setProfile(incognito_profile)
        self.jquery_manager = JQueryManager(incognito_profile)

    def setup_interceptors(self):
        """Setup interceptor untuk ad blocking dan safe browsing"""
        if self.ad_block_interceptor and self.safe_browsing:
            ad_blocker = self.ad_block_interceptor()
            safe_browsing = self.safe_browsing()
            if ad_blocker and safe_browsing:
                combined_interceptor = CombinedInterceptor(ad_blocker, safe_browsing)
                self.profile().setUrlRequestInterceptor(combined_interceptor)

    def apply_privacy_settings(self):
        """Terapkan pengaturan privasi"""
        if self.privacy_settings:
            privacy_settings = self.privacy_settings()
            if privacy_settings:
                privacy_settings.apply_to_page(self)

    def set_user_agent(self):
        """Set user agent"""
        user_agent_string = self._get_user_agent_string()
        self.profile().setHttpUserAgent(user_agent_string)

    @lru_cache(maxsize=1)
    def _get_user_agent_string(self):
        """Helper method untuk mendapatkan user agent string"""
        if self.user_agent:
            user_agent = self.user_agent()
            if user_agent:
                if hasattr(user_agent, 'user_agent'):
                    return user_agent.user_agent
                elif hasattr(user_agent, 'get_current_user_agent'):
                    return user_agent.get_current_user_agent()
        return self.profile().httpUserAgent()

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        """Validasi dan filter permintaan navigasi"""
        if isinstance(url, QUrl):
            url_string = url.toString()
        else:
            url_string = str(url)

        self.logger.debug(f"Navigation request to: {url_string}")

        if not url_string.startswith(("http://", "https://")):
            self.logger.warning(f"Blocked navigation to non-HTTP URL: {url_string}")
            return False

        return True

    def clear_browsing_data(self):
        """Membersihkan data browsing"""
        self.profile().clearAllVisitedLinks()
        self.profile().clearHttpCache()
        self.profile().cookieStore().deleteAllCookies()

    def set_javascript_enabled(self, enabled):
        """Mengaktifkan atau menonaktifkan JavaScript"""
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, enabled)

    def featurePermissionRequested(self, securityOrigin, feature):
        """Handler untuk permintaan izin fitur"""
        self.logger.debug(f"Feature permission requested: {feature} for {securityOrigin.toString()}")
        self.grantFeaturePermission(securityOrigin, feature, True)

    def javaScriptAlert(self, securityOrigin, msg):
        """Handler untuk alert JavaScript"""
        self.logger.debug(f"JavaScript alert: {msg} for {securityOrigin.toString()}")

    def javaScriptConfirm(self, securityOrigin, msg):
        """Handler untuk konfirmasi JavaScript"""
        self.logger.debug(f"JavaScript confirm: {msg} for {securityOrigin.toString()}")

    def javaScriptPrompt(self, securityOrigin, msg, default_value):
        """Handler untuk prompt JavaScript"""
        self.logger.debug(f"JavaScript prompt: {msg} for {securityOrigin.toString()}")

class CombinedInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, ad_blocker, safe_browsing):
        self.ad_blocker = ad_blocker
        self.safe_browsing = safe_browsing

    def interceptRequest(self, info):
        self.ad_blocker.interceptRequest(info)
        self.safe_browsing.interceptRequest(info)