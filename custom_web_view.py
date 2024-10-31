from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage

class CustomWebView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._page = None
        
    def setPage(self, page):
        if self._page:
            self._page.deleteLater()
        self._page = page
        super().setPage(page)

    def closeEvent(self, event):
        if self._page:
            # Bersihkan cache dan data saat tab ditutup
            profile = self._page.profile()
            if not profile.isOffTheRecord():  # Jika bukan mode incognito
                profile.clearHttpCache()
            self._page.deleteLater()
            self._page = None
        super().closeEvent(event)

class CustomWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            print(f"JavaScript Error: {message} at line {lineNumber} in {sourceID}")
        
    def certificateError(self, error):
        print(f"Certificate Error: {error.errorDescription()}")
        return False