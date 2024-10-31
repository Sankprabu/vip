import sys
import json
import os
import re
from urllib.parse import urlparse

from PyQt6.QtWidgets import (QApplication, QMainWindow, QToolBar, QStatusBar, QLineEdit, QMessageBox, 
                             QTabWidget, QWidget, QVBoxLayout, QPushButton, QDialog, QCheckBox, 
                             QDialogButtonBox, QProgressBar, QMenu, QToolButton, QMenuBar, QInputDialog)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import QUrl, Qt, QSize
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QStyle
from user_agents import UserAgentManager
from profile_manager import ProfileManager
from custom_web_view import CustomWebView
from profile_manager import ProfileManager
from PyQt6.QtCore import QCoreApplication
import gc
from download_manager import DownloadManager
from cache_manager import CacheManager
from data_saver import DataSaver
from browser_styles import BrowserStyles
from client_hints_manager import ClientHintsManager
from client_hints_manager import ClientHintsManager
from privacy_settings import PrivacySettings
from jquery_manager import JQueryManager
from custom_web_page import CustomWebPage
from PyQt6.QtGui import QIcon
from about import AboutDialog

class SettingsMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        self.main_window = parent
        self.client_hints_manager = ClientHintsManager()
        self.privacy_settings = PrivacySettings(QWebEngineProfile.defaultProfile())
        self.init_ui()
        self.is_mobile_mode = False  # Set default ke desktop mode

    def init_ui(self):
        # Menu yang sudah ada
        account_menu = QMenu("Account", self)
        self.addMenu(account_menu)

        login_action = QAction("Login", self)
        login_action.triggered.connect(self.login)
        account_menu.addAction(login_action)

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        account_menu.addAction(logout_action)

        # Tambahkan submenu untuk Client Hints
        client_hints_menu = QMenu("Client Hints", self)
        self.addMenu(client_hints_menu)

        # Toggle Client Hints
        self.client_hints_action = QAction("Enable Client Hints", self)
        self.client_hints_action.setCheckable(True)
        self.client_hints_action.triggered.connect(self.toggle_client_hints)
        client_hints_menu.addAction(self.client_hints_action)

         # Menu Privacy Settings
        privacy_menu = QMenu("Privacy", self)
        self.addMenu(privacy_menu)

        # Private Browsing Toggle
        self.private_mode_action = QAction("Private Browsing", self)
        self.private_mode_action.setCheckable(True)
        self.private_mode_action.triggered.connect(self.toggle_private_mode)
        privacy_menu.addAction(self.private_mode_action)

        # DNT Toggle
        self.dnt_action = QAction("Do Not Track (DNT)", self)
        self.dnt_action.setCheckable(True)
        self.dnt_action.triggered.connect(self.toggle_dnt)
        privacy_menu.addAction(self.dnt_action)

        # GPC Toggle
        self.gpc_action = QAction("Global Privacy Control", self)
        self.gpc_action.setCheckable(True)
        self.gpc_action.triggered.connect(self.toggle_gpc)
        privacy_menu.addAction(self.gpc_action)

        # Mode selector untuk Client Hints
        client_hints_mode_menu = QMenu("Client Hints Mode", self)
        client_hints_menu.addMenu(client_hints_mode_menu)

        # Tambahkan mode-mode yang tersedia
        modes = ["default", "hide", "manipulate", "randomize"]
        for mode in modes:
            mode_action = QAction(mode.capitalize(), self)
            mode_action.triggered.connect(lambda checked, m=mode: self.change_client_hints_mode(m))
            client_hints_mode_menu.addAction(mode_action)

        # Menu yang sudah ada
        new_window_action = QAction("Open New Window", self)
        new_window_action.triggered.connect(self.open_new_window)
        self.addAction(new_window_action)

        delete_data_action = QAction("Delete Browsing Data", self)
        delete_data_action.triggered.connect(self.delete_browsing_data)
        self.addAction(delete_data_action)

        find_action = QAction("Find in Page", self)
        find_action.triggered.connect(self.find_in_page)
        self.addAction(find_action)

        self.dark_mode_action = QAction("Dark Mode", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        self.addAction(self.dark_mode_action)

    # Tambahkan About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        self.addAction(about_action)  # Tambahkan action ke menu

    def show_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    # Tambahkan method untuk privacy settings
    def toggle_private_mode(self, checked):
        if checked:
            self.privacy_settings.enable_private_browsing()
            if hasattr(self.main_window, 'status_bar'):
                self.main_window.status_bar.showMessage("Private Browsing enabled")
        else:
            self.privacy_settings.disable_private_browsing()
            if hasattr(self.main_window, 'status_bar'):
                self.main_window.status_bar.showMessage("Private Browsing disabled")

    def toggle_dnt(self, checked):
        self.privacy_settings.set_dnt_enabled(checked)
        if hasattr(self.main_window, 'status_bar'):
            self.main_window.status_bar.showMessage(
                f"Do Not Track {'enabled' if checked else 'disabled'}"
            )

    def toggle_gpc(self, checked):
        self.privacy_settings.set_gpc_enabled(checked)
        if hasattr(self.main_window, 'status_bar'):
            self.main_window.status_bar.showMessage(
                f"Global Privacy Control {'enabled' if checked else 'disabled'}"
            )

    def toggle_client_hints(self):
        if self.client_hints_manager.is_active:
            self.client_hints_manager.deactivate()
            self.client_hints_action.setText("Enable Client Hints")
            if hasattr(self.main_window, 'status_bar'):
                self.main_window.status_bar.showMessage("Client Hints dinonaktifkan")
        else:
            self.client_hints_manager.activate()
            self.client_hints_action.setText("Disable Client Hints")
            if hasattr(self.main_window, 'status_bar'):
                self.main_window.status_bar.showMessage("Client Hints diaktifkan")
        self.apply_client_hints_to_all_tabs()

    def change_client_hints_mode(self, mode):
        self.client_hints_manager.set_mode(mode)
        self.apply_client_hints_to_all_tabs()
        if hasattr(self.main_window, 'status_bar'):
            self.main_window.status_bar.showMessage(f"Client Hints mode changed to: {mode}")

    def apply_client_hints_to_all_tabs(self):
        if hasattr(self.main_window, 'tab_widget'):
            for i in range(self.main_window.tab_widget.count()):
                tab = self.main_window.tab_widget.widget(i)
                web_view = tab.findChild(QWebEngineView)
                if web_view:
                    profile = web_view.page().profile()
                    self.client_hints_manager.apply_to_profile(profile)

    # Metode-metode yang sudah ada tetap sama
    def login(self):
        email, ok = QInputDialog.getText(self.main_window, "Login", "Enter your email:")
        if ok:
            password, ok = QInputDialog.getText(self.main_window, "Login", "Enter your password:", QLineEdit.EchoMode.Password)
            if ok:
                QMessageBox.information(self.main_window, "Login", f"Logged in as {email}")

    def logout(self):
        QMessageBox.information(self.main_window, "Logout", "You have been logged out")

    def open_new_window(self):
        self.main_window.new_window()

    def delete_browsing_data(self):
        reply = QMessageBox.question(
            self.main_window,
            "Delete Browsing Data",
            "Are you sure you want to delete browsing data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.main_window.delete_browsing_data()

    def find_in_page(self):
        text, ok = QInputDialog.getText(self.main_window, "Find in Page", "Enter text to find:")
        if ok and text:
            self.main_window.find_in_page(text)

    def toggle_dark_mode(self):
        self.main_window.toggle_dark_mode()   

    

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(flags=Qt.WindowType.Window)
        self.setWindowTitle("ViP Browser")
        self.resize(1000, 600)
        self.dark_mode = False
        self.browsing_data = []
        self.profile_manager = ProfileManager()
        self.bookmarks = self.load_bookmarks()
        self.bookmark_menu = self.menuBar().addMenu("Bookmarks")
        self.update_bookmark_menu()
        self.setStyleSheet(BrowserStyles.get_style(dark_mode=True))  # Ganti dark_mode ke True untuk mode gelap
        self.jquery_manager = JQueryManager()
        self.is_mobile_mode = False  # Set default ke desktop mode
        self.history = self.load_history()
        self.create_history_menu()

        self.create_menus()
        
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        self.settings_menu = SettingsMenu(self)
        self.menu_bar.addMenu(self.settings_menu)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.is_mobile_mode = False
        self.toggle_mode_button = QPushButton("Desktop Mode")
        self.toggle_mode_button.clicked.connect(self.toggle_mode)
        self.toolbar.addWidget(self.toggle_mode_button)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(120)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)

        self.add_tab_button = QPushButton("+")
        self.add_tab_button.clicked.connect(lambda: self.add_new_tab())
        self.toolbar.addWidget(self.add_tab_button)

        self.incognito_tab_button = QPushButton("Incognito")
        self.incognito_tab_button.clicked.connect(self.add_incognito_tab)
        self.toolbar.addWidget(self.incognito_tab_button)

        self.back_button = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        self.back_button.triggered.connect(self.navigate_back)
        self.toolbar.addAction(self.back_button)

        self.forward_button = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        self.forward_button.triggered.connect(self.navigate_forward)
        self.toolbar.addAction(self.forward_button)

        self.reload_button = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        self.reload_button.triggered.connect(self.reload_current_tab)
        self.toolbar.addAction(self.reload_button)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search terms")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.url_bar)

        self.bookmark_button = QPushButton("Bookmarks")
        self.bookmark_button.clicked.connect(self.show_bookmarks)
        self.toolbar.addWidget(self.bookmark_button)

        self.add_new_tab()

        self.bookmark_menu = QMenu("Bookmarks ", self)
        self.menuBar().addMenu(self.bookmark_menu)

        settings_icon = QIcon.fromTheme("preferences-system")
        if settings_icon.isNull():
            settings_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)

        self.settings_button = QToolButton(self)
        self.settings_button.setIcon(settings_icon)
        self.settings_button.setToolTip("Settings")
        self.settings_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.toolbar.addWidget(self.settings_button)

        self.create_settings_menu()
        self.load_settings()

        self.profile_manager = ProfileManager()
        self.tab_manager = ProfileManager(self.tab_widget, self.profile_manager)
        new_profile = self.profile_manager.create_web_profile()
        new_tab = QWebEngineView()
        new_tab.setPage(QWebEnginePage(new_profile, new_tab))

        # Inisialisasi manager
        self.download_manager = DownloadManager(self)
        self.cache_manager = CacheManager()
        self.data_saver = DataSaver()
        
        # Setup signals
        self.download_manager.download_started.connect(self.on_download_started)
        self.download_manager.download_finished.connect(self.on_download_finished)
        self.download_manager.download_failed.connect(self.on_download_failed)
        self.set_browser_icon()

    def set_browser_icon(self):
        app_icon = QIcon("assets/browser_icon.ico")
        self.setWindowIcon(app_icon)

    def on_download_started(self, filename):
        self.status_bar.showMessage(f"Mulai mengunduh: {filename}")

    def on_download_finished(self, filename):
        self.status_bar.showMessage(f"Selesai mengunduh: {filename}")

    def on_download_failed(self, filename, error):
        self.status_bar.showMessage(f"Gagal mengunduh {filename}: {error}")

    def toggle_data_saver(self):
        is_enabled = self.data_saver.toggle()
        status = "aktif" if is_enabled else "nonaktif"
        self.status_bar.showMessage(f"Mode hemat data {status}")

    def closeEvent(self, event):
        # Bersihkan semua profil saat aplikasi ditutup
        self.profile_manager.cleanup_profiles()
        super().closeEvent(event)

    def create_web_profile(self, is_mobile=False):
        profile = QWebEngineProfile()
        # ... kode lainnya ...
    
        # Batasi ukuran cache (dalam bytes)
        profile.setHttpCacheMaximumSize(100 * 1024 * 1024)  # 100MB
    
        return profile
    
    def clear_browsing_data(self):
    
        for profile in self.profiles:
            if profile:
                profile.clearAllVisitedLinks()
                profile.clearHttpCache()
                profile.clearIconDatabase()

    def load_bookmarks(self):
        if os.path.exists("bookmarks.json"):
            with open("bookmarks.json", "r") as f:
                return json.load(f)
        return []

    def save_bookmarks(self):
        with open("bookmarks.json", "w") as f:
            json.dump(self.bookmarks, f)

    def update_bookmark_menu(self):
        self.bookmark_menu.clear()
        for bookmark in self.bookmarks:
            action = QAction(bookmark['title'], self)
            action.triggered.connect(lambda _, url=bookmark['url']: self.load_url(url))
            self.bookmark_menu.addAction(action)
        
        self.bookmark_menu.addSeparator()
        add_bookmark_action = QAction("Add Bookmark", self)
        add_bookmark_action.triggered.connect(self.add_bookmark)
        self.bookmark_menu.addAction(add_bookmark_action)

    def add_bookmark(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            web_view = current_tab.findChild(QWebEngineView)
            if web_view:
                url = web_view.url().toString()
                title = web_view.page().title()
                self.bookmarks.append({"url": url, "title": title})
                self.save_bookmarks()
                self.update_bookmark_menu()

    def load_url(self, url):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            web_view = current_tab.findChild(QWebEngineView)
            if web_view:
                web_view.load(QUrl(url))

    def load_history(self):
        if os.path.exists("history.json"):
            with open("history.json", "r") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open("history.json", "w") as f:
            json.dump(self.history, f)

    def create_history_menu(self):
        self.history_menu = QMenu ("History", self)
        self.menuBar().addMenu(self.history_menu)
        self.update_history_menu()

    def update_history_menu(self):
        self.history_menu.clear()
        for item in reversed(self.history[-10:]):  # Show last 10 items
            action = QAction(item['title'], self)
            action.triggered.connect(lambda _, url=item['url']: self.load_url(url))
            self.history_menu.addAction(action)
        
        self.history_menu.addSeparator()
        clear_history_action = QAction("Clear History", self)
        clear_history_action.triggered.connect(self.clear_history)
        self.history_menu.addAction(clear_history_action)

    def add_to_history(self, url, title):
        self.history.append({"url": url, "title": title})
        self.save_history()
        self.update_history_menu()

    def clear_history(self):
        self.history.clear()
        self.save_history()
        self.update_history_menu()

    def setup_logging(self):
        # Konfigurasi logging untuk seluruh aplikasi
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),  # Output ke konsol
                logging.FileHandler('vip_browser.log')  # Output ke file
            ]
        )
        self.logger = logging.getLogger('VipBrowser.MainWindow')
        self.logger.info("Aplikasi ViP Browser dimulai")

    def add_new_tab(self, title="New Tab", url="https://www.google.com", incognito=False):
        # Validasi URL
        if not self.validate_url(url):
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid URL.")
            return

        # Buat web view dan atur koneksi dasar
        web_view = QWebEngineView()
        web_view.loadFinished.connect(self.update_tab_title)
        web_view.loadStarted.connect(self.start_loading)
        web_view.loadFinished.connect(self.finish_loading)
        web_view.setFixedSize(QSize(16777215, 16777215))  # QWIDGETSIZE_MAX
    # Atur profile berdasarkan mode incognito
        profile = QWebEngineProfile() if incognito else QWebEngineProfile.defaultProfile()
    
    # Buat custom page dengan jQuery manager
        page = CustomWebPage(
            profile=profile,
            ad_block_interceptor=getattr(self, 'ad_blocker', None),
            privacy_settings=getattr(self, 'privacy_settings', None),
            incognito_mode=getattr(self, 'incognito_mode', None),
            safe_browsing=getattr(self, 'safe_browsing', None),
            user_agent=getattr(self, 'user_agent', None),
            parent=web_view
        )
    
    # Set jQuery manager ke page
        page.jquery_manager = self.jquery_manager
    
    # Set page ke web view
        web_view.setPage(page)

    # Atur user agent
        user_agent = UserAgentManager.get_random_ua(self.is_mobile_mode)
        page.profile().setHttpUserAgent(user_agent)

    # Konfigurasi mode mobile jika aktif
        if self.is_mobile_mode:
            web_view.setFixedSize(QSize(360, 640))
            web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)

    # Suntikkan jQuery dan atur callback pemeriksaan
        self.jquery_manager.suntik_jquery_dengan_percobaan(web_view)
        web_view.loadFinished.connect(
            lambda: self.jquery_manager.periksa_jquery_dimuat(web_view)
        )

    # Muat URL
        web_view.load(QUrl(url))

    # Buat dan atur tab
        tab_content = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(web_view)
        tab_content.setLayout(layout)

    # Tambahkan tab baru dan aktifkan
        index = self.tab_widget.addTab(tab_content, title)
        self.tab_widget.setCurrentIndex(index)

        return web_view
    
    def add_incognito_tab(self):
        try:
            tab_container = QWidget()
            layout = QVBoxLayout(tab_container)
        
            web_view = QWebEngineView()
            incognito_profile = self.profile_manager.create_incognito_profile()
        
            if incognito_profile:
                page = QWebEnginePage(incognito_profile, web_view)
                web_view.setPage(page)
            
                layout.addWidget(web_view)
                layout.setContentsMargins(0, 0, 0, 0)
            
                web_view.loadFinished.connect(self.update_tab_title)
                web_view.loadStarted.connect(self.start_loading)
                web_view.loadFinished.connect(self.finish_loading)
            
                web_view.load(QUrl("https://www.google.com"))
            
                index = self.tab_widget.addTab(tab_container, "Incognito")
                self.tab_widget.setCurrentIndex(index)
            
                tab_container.incognito_profile = incognito_profile
            else:
                raise Exception("Failed to create incognito profile")
            
        except Exception as e:
            self.logger.error(f"Error creating incognito tab: {e}")

    def create_incognito_profile(self):
    
        try:
            profile = QWebEngineProfile()
            profile.setOffTheRecord(True)  # Aktifkan mode incognito
        
            # Konfigurasi profil
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True)
        
            # Set random user agent
            profile.setHttpUserAgent(UserAgentManager.get_random_ua(False))
        
        # Gunakan cache memory untuk incognito
            profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
        
        # Tambahkan ke daftar profil yang dikelola
            self.profiles.append(profile)
            self.logger.info("Created new incognito profile")
        
            return profile
        
        except Exception as e:
            self.logger.error(f"Error creating incognito profile: {e}")
            return None


    def navigate_to_url(self):
        url = self.url_bar.text().strip()
    
        # Cek apakah input kosong
        if not url:
            return
    
    # Cek apakah URL valid
        if self.validate_url(url):
            # Tambahkan https:// jika tidak ada protokol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
        else:
        # Jika bukan URL valid, gunakan pencarian Google
            url = f'https://www.google.com/search?q={url}'
    
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            web_view = current_tab.findChild(QWebEngineView)
            if web_view:
                web_view.setUrl(QUrl(url))

    def validate_url(self, url):
        # Pola sederhana untuk memvalidasi URL
        url_pattern = re.compile(
            r'^(?:http(s)?:\/\/)?'  # protokol http(s)
         r'(?:(?:[\w-]+\.)+[a-zA-Z]{2,})'  # domain
            r'(?:\/[\w\.-]*)*\/?$'  # path
        )
    
     # Hapus spasi di awal dan akhir
        url = url.strip()
    
        # Cek apakah mengandung spasi (kemungkinan query pencarian)
        if ' ' in url:
            return False
        
    # Cek domain umum
        common_domains = ['.com', '.net', '.org', '.edu', '.gov', '.co', '.co.id', '.id']
        has_common_domain = any(url.endswith(domain) for domain in common_domains)
    
    # Kembalikan True jika cocok dengan pola URL dan/atau memiliki domain umum
        return bool(url_pattern.match(url)) or has_common_domain

    def navigate_back(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            web_view = current_tab.findChild(QWebEngineView)
            if web_view and web_view.page().history().canGoBack():
                web_view.back()

    def navigate_forward(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            web_view = current_tab.findChild(QWebEngineView)
            if web_view and web_view.page().history().canGoForward():
                try:
                    web_view.page().triggerAction(QWebEnginePage.WebAction.Forward)
                except AttributeError:
                    web_view.forward()

    def reload_current_tab(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            web_view = current_tab.findChild(QWebEngineView)
            if web_view :
                web_view.page().triggerAction(QWebEnginePage.WebAction.Reload)

    def toggle_mode(self):
        self.is_mobile_mode = not self.is_mobile_mode
        if self.is_mobile_mode:
            self.set_mobile_mode()
            self.toggle_mode_button.setText("Desktop Mode")
        else:
            self.set_desktop_mode()
            self.toggle_mode_button.setText("Mobile Mode")

    def set_mobile_mode(self):
        mobile_user_agent = UserAgentManager.get_random_mobile_ua()
        QWebEngineProfile.defaultProfile().setHttpUserAgent(mobile_user_agent)
        self.apply_style()

        for i in range(self.tab_widget.count()):
            web_view = self.tab_widget.widget(i).findChild(QWebEngineView)
            if web_view:
                web_view.setFixedSize(QSize(360, 640))
                web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
                web_view.page().profile().setHttpUserAgent(mobile_user_agent)

    def set_desktop_mode(self):
        desktop_user_agent = UserAgentManager.get_random_desktop_ua()
        QWebEngineProfile.defaultProfile().setHttpUserAgent(desktop_user_agent)
    
        # Set default desktop settings untuk semua tab
        for i in range(self.tab_widget.count()):
            web_view = self.tab_widget.widget(i).findChild(QWebEngineView)
            if web_view:
                settings = web_view.settings()
                settings.setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
                web_view.setFixedSize(QSize(16777215, 16777215))
                web_view.page().profile().setHttpUserAgent(desktop_user_agent)
            
                # Set viewport untuk desktop mode
                script = """
                var viewport = document.querySelector('meta[name="viewport"]');
                if (viewport) viewport.remove();
            """
                web_view.page().runJavaScript(script)






    def delete_browsing_data(self):
        self.browsing_data.clear()  # Clear the browsing data
        print("Browsing data deleted.")

    def new_window(self):
        window = MainWindow()
        window.show()

    def find_in_page(self, text):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            web_view = current_tab.findChild(QWebEngineView)
            if web_view:
                web_view.page().findText(text)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_style()
        self.save_settings()
        self.settings_menu.dark_mode_action.setChecked(self.dark_mode)

    def save_settings(self):
        settings = {
            "desktop_mode": not self.is_mobile_mode,
            "dark_mode": self.dark_mode
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)

    def apply_style(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #1e1e1e;
                }
                QMenuBar::item:selected {
                    background-color: #3a3a3a;
                }
                QMenu {
                    background-color: #2b2b2b;
                    border: 1px solid #3a3a3a;
                }
                QMenu::item:selected {
                    background-color: #3a3a3a;
                }
                QToolBar {
                    background-color: # 1e1e1e;
                    border: none;
                }
                QPushButton {
                    background-color: #3a3a3a;
                    color: #ffffff;
                    border: none;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QTabWidget::pane {
                    border: 1px solid #3a3a3a;
                }
                QTabBar::tab {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #3a3a3a;
                    padding: 5px;
                }
                QTabBar::tab:selected {
                    background-color: #3a3a3a;
                }
                QLineEdit {
                    background-color: #3a3a3a;
                    color: #ffffff;
                    border: 1px solid #4a4a4a;
                }
            """)
        else:
            self.setStyleSheet("")  # Reset to default light style

        # Apply style to all open tabs
        for i in range(self.tab_widget.count()):
            web_view = self.tab_widget.widget(i).findChild(QWebEngineView)
            if web_view:
                web_view.page().setBackgroundColor(Qt.GlobalColor.white if not self.dark_mode else Qt.GlobalColor.black)

    def create_settings_menu(self):
        settings_menu = QMenu(self)

        account_action = QAction("Account", self)
        account_action.triggered.connect(self.open_account_settings)
        settings_menu.addAction(account_action)

        general_action = QAction("General", self)
        general_action.triggered.connect(self.open_general_settings)
        settings_menu.addAction(general_action)

        find_edit_action = QAction("Find and Edit", self)
        find_edit_action.triggered.connect(self.open_find_edit_settings)
        settings_menu.addAction(find_edit_action)

        settings_menu.addSeparator()

        full_settings_action = QAction("All Settings", self)
        full_settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(full_settings_action)

        self.settings_button.setMenu(settings_menu)

    def create_menus(self):
        file_menu = self.menuBar().addMenu("File")
        
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        file_menu.addAction(new_tab_action)

        incognito_action = QAction("Incognito Tab", self)
        incognito_action.triggered.connect(self.add_incognito_tab)
        file_menu.addAction(incognito_action)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = self.menuBar().addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def open_account_settings(self):
        print("Opening Account Settings")

    def open_general_settings(self):
        print("Opening General Settings")

    def open_find_edit_settings(self):
        print("Opening Find and Edit Settings")

    def open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        checkbox = QCheckBox("Enable desktop mode by default")
        layout.addWidget(checkbox)

        checkbox_dark_mode = QCheckBox("Enable dark mode")
        checkbox_dark_mode.setChecked(self.dark_mode)
        checkbox_dark_mode.stateChanged.connect(self.toggle_dark_mode)
        layout.addWidget(checkbox_dark_mode)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec():
            settings = {"desktop_mode": checkbox.isChecked(), "dark_mode": checkbox_dark_mode.isChecked()}
            with open("settings.json", "w") as f:
                json.dump(settings, f)

    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    # Default ke desktop mode (False untuk is_mobile_mode)
                    self.is_mobile_mode = settings.get("mobile_mode", False)
                    self.dark_mode = settings.get("dark_mode", False)
            else:
                # Jika file settings tidak ada, gunakan defaults
                self.is_mobile_mode = False
                self.dark_mode = False
            
            # Terapkan pengaturan
            if not self.is_mobile_mode:
                self.set_desktop_mode()
            self.apply_style()
            if hasattr(self, 'settings_menu'):
                self.settings_menu.dark_mode_action.setChecked(self.dark_mode)
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Fallback ke desktop mode jika terjadi error
            self.is_mobile_mode = False
            self.set_desktop_mode()




    def show_about(self):
        QMessageBox.about(self, "About", "ViP Browser v1.0")

    def show_bookmarks(self):
        pass

    def close_tab(self, index):
   
        try:
        # Ambil widget tab
            tab = self.tab_widget.widget(index)
            if tab:
            # Cek apakah ini tab incognito
                if hasattr(tab, 'incognito_profile'):
                # Bersihkan profil incognito
                    self.profile_manager.cleanup_single_profile(tab.incognito_profile)
            
            # Ambil web view
                web_view = tab.findChild(QWebEngineView)
                if web_view:
                # Bersihkan halaman
                    page = web_view.page()
                    if page:
                        page.setParent(None)
                        page.deleteLater()
                
                # Bersihkan web view
                    web_view.setParent(None)
                    web_view.deleteLater()
            
            # Hapus tab
                self.tab_widget.removeTab(index)
                tab.deleteLater()
            
            # Force garbage collection
                gc.collect()
                QCoreApplication.processEvents()
            
        except Exception as e:
            print(f"Error closing tab: {e}")
     

    def update_tab_title(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            web_view = current_tab.findChild(QWebEngineView)
            if web_view:
                title = web_view.page().title()
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), title)

    def start_loading(self):
        self.progress_bar.show()
        self.progress_bar.setValue(0)

    def finish_loading(self):
        self.progress_bar.hide()
        self.progress_bar.setValue(100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/browser_icon.ico"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())