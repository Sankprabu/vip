from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtCore import QObject, QTimer, QCoreApplication
from user_agents import UserAgentManager
import logging
import gc

class ProfileManager(QObject):
    def __init__(self, tab_widget=None, profile_manager=None):
        super().__init__()
        self.profiles = []
        self.tab_widget = tab_widget
        self.profile_manager = profile_manager
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def create_incognito_profile(self):
        """Membuat profil khusus untuk mode incognito"""
        try:
            profile = QWebEngineProfile()
            
            # Konfigurasi untuk mode incognito tanpa menggunakan setOffTheRecord
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, False)  # Disable local storage
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True)
            
            # Konfigurasi privasi tambahan
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, False)
            
            # Set random user agent
            profile.setHttpUserAgent(UserAgentManager.get_random_ua(False))
            
            # Konfigurasi cache dan cookies
            profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
            
            # Batasi ukuran cache
            profile.setHttpCacheMaximumSize(0)  # Disable disk cache
            
            self.profiles.append(profile)
            self.logger.info("Created new incognito profile")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error creating incognito profile: {e}")
            return None

    def force_cleanup_page(self, page):
        """Pembersihan paksa untuk halaman web"""
        if page:
            self.logger.info("Force cleaning web page")
            page.action(page.WebAction.Stop).trigger()
            page.setParent(None)
            page.deleteLater()
            QCoreApplication.processEvents()

    def force_cleanup_widget(self, widget):
        """Pembersihan paksa untuk widget"""
        if widget:
            self.logger.info("Force cleaning widget")
            if hasattr(widget, 'page'):
                self.force_cleanup_page(widget.page())
            widget.setParent(None)
            widget.deleteLater()
            QCoreApplication.processEvents()

    def cleanup_single_profile(self, profile):
        """Pembersihan menyeluruh untuk satu profil"""
        if profile in self.profiles:
            self.logger.info(f"Cleaning up profile {profile}")
            
            # Bersihkan semua page terkait
            if self.tab_widget:
                for i in range(self.tab_widget.count() - 1, -1, -1):
                    widget = self.tab_widget.widget(i)
                    if widget:
                        page = widget.page()
                        if page and page.profile() == profile:
                            self.logger.info(f"Cleaning tab {i}")
                            self.force_cleanup_page(page)
                            self.force_cleanup_widget(widget)
                            self.tab_widget.removeTab(i)
                            QCoreApplication.processEvents()

            # Tunggu sebentar untuk memastikan semua cleanup selesai
            QTimer.singleShot(100, lambda: self._finish_profile_cleanup(profile))

    def _finish_profile_cleanup(self, profile):
        """Menyelesaikan pembersihan profil"""
        try:
            if profile in self.profiles:
                profile.clearHttpCache()
                self.profiles.remove(profile)
                profile.deleteLater()
                gc.collect()
                QCoreApplication.processEvents()
                self.logger.info("Profile cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during profile cleanup: {e}")

    def switch_to_incognito(self, current_tab_index):
        """Beralih ke mode incognito"""
        try:
            # Bersihkan tab dan profil yang ada
            if current_tab_index >= 0:
                widget = self.tab_widget.widget(current_tab_index)
                if widget:
                    old_page = widget.page()
                    if old_page:
                        old_profile = old_page.profile()
                        self.cleanup_single_profile(old_profile)

            # Buat profil incognito baru
            new_profile = self.create_incognito_profile()
            return new_profile

        except Exception as e:
            self.logger.error(f"Error switching to incognito: {e}")
            return None

    def cleanup_profiles(self):
        """Membersihkan semua profil"""
        self.logger.info("Starting cleanup of all profiles")
        for profile in self.profiles[:]:
            self.cleanup_single_profile(profile)
        self.profiles.clear()
        gc.collect()
        QCoreApplication.processEvents()
        self.logger.info("All profiles cleaned up")

    def safe_cleanup(self):
        """Pembersihan aman saat aplikasi ditutup"""
        self.logger.info("Starting safe cleanup")
        QTimer.singleShot(500, self.cleanup_profiles)


    def create_web_profile(self, is_mobile=False):
        """Membuat profil web baru"""
        try:
            profile = QWebEngineProfile()
            
            # Konfigurasi default untuk profil normal
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True)
            
            # Set user agent
            profile.setHttpUserAgent(UserAgentManager.get_random_ua(is_mobile))
            
            # Konfigurasi cache
            profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
            
            self.profiles.append(profile)
            self.logger.info("Created new web profile")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error creating web profile: {e}")
            return None