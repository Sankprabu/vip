from PyQt6.QtWebEngineCore import QWebEngineProfile
import os
import shutil

class CacheManager:
    def __init__(self):
        self.max_cache_size = 100 * 1024 * 1024  # 100MB default
        self.setup_cache()

    def setup_cache(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpCacheMaximumSize(self.max_cache_size)
        
    def set_cache_size(self, size_mb):
        """Set cache size in megabytes"""
        self.max_cache_size = size_mb * 1024 * 1024
        self.setup_cache()

    def clear_cache(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()
        
    def get_cache_size(self):
        """Return current cache size in bytes"""
        cache_path = QWebEngineProfile.defaultProfile().cachePath()
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(cache_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def cleanup_old_cache(self, days_old=7):
        """Remove cache files older than specified days"""
        cache_path = QWebEngineProfile.defaultProfile().cachePath()
        current_time = time.time()
        
        for dirpath, dirnames, filenames in os.walk(cache_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.stat(fp).st_mtime < (current_time - (days_old * 86400)):
                    os.remove(fp)