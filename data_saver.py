from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings

class DataSaver:
    def __init__(self):
        self.is_enabled = False
        self.profile = QWebEngineProfile.defaultProfile()
        self.settings = self.profile.settings()

    def enable(self):
        self.is_enabled = True
        # Nonaktifkan load gambar otomatis
        self.settings.setAttribute(
            QWebEngineSettings.WebAttribute.AutoLoadImages, 
            False
        )
        # Nonaktifkan autoplay media
        self.settings.setAttribute(
            QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, 
            True
        )
        # Kurangi kualitas gambar
        self.profile.setHttpCacheType(
            QWebEngineProfile.HttpCacheType.MemoryHttpCache
        )
        # Nonaktifkan prefetch
        self.settings.setAttribute(
            QWebEngineSettings.WebAttribute.PrefetchLinkEnabled,
            False
        )

    def disable(self):
        self.is_enabled = False
        # Aktifkan kembali fitur default
        self.settings.setAttribute(
            QWebEngineSettings.WebAttribute.AutoLoadImages, 
            True
        )
        self.settings.setAttribute(
            QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture,
            False
        )
        self.profile.setHttpCacheType(
            QWebEngineProfile.HttpCacheType.DiskHttpCache
        )
        self.settings.setAttribute(
            QWebEngineSettings.WebAttribute.PrefetchLinkEnabled,
            True
        )

    def toggle(self):
        if self.is_enabled:
            self.disable()
        else:
            self.enable()
        return self.is_enabled

    def get_status(self):
        return "Aktif" if self.is_enabled else "Nonaktif"