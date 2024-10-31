from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QObject, pyqtSignal

class DownloadManager(QObject):
    download_started = pyqtSignal(str)
    download_finished = pyqtSignal(str)
    download_failed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.download_path = ""
        self.downloads = []
        self.setup_download_handlers()

    def setup_download_handlers(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.handle_download)

    def set_download_path(self, parent_window):
        path = QFileDialog.getExistingDirectory(
            parent_window, 
            "Pilih Lokasi Download",
            self.download_path
        )
        if path:
            self.download_path = path
            QWebEngineProfile.defaultProfile().setDownloadPath(path)
            return True
        return False

    def handle_download(self, download):
        try:
            if not self.download_path:
                if not self.set_download_path(self.parent()):
                    download.cancel()
                    return

            download.accept()
            self.downloads.append(download)
            
            filename = download.suggestedFileName()
            self.download_started.emit(filename)

            download.finished.connect(
                lambda: self.on_download_finished(filename)
            )
            download.downloadProgress.connect(
                lambda received, total: self.update_progress(filename, received, total)
            )

        except Exception as e:
            self.download_failed.emit(filename, str(e))

    def on_download_finished(self, filename):
        self.download_finished.emit(filename)

    def update_progress(self, filename, received, total):
        progress = (received / total) * 100 if total > 0 else 0
        print(f"Download progress for {filename}: {progress:.1f}%")

    def cancel_all_downloads(self):
        for download in self.downloads:
            download.cancel()
        self.downloads.clear()