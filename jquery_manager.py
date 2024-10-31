from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView
import logging
import time

class JQueryManager:
    def __init__(self, profile=None):
        self.logger = logging.getLogger('VipBrowser.JQueryManager')
        self.jquery_cdn_url = "https://code.jquery.com/jquery-3.6.0.min.js"
        self.profile = profile if profile else QWebEngineProfile.defaultProfile()
        self.jquery_loaded = False
        self.jquery_version = None

    def suntik_jquery_dengan_percobaan(self, web_object):
        script = f"""
        (function() {{
            if (typeof jQuery === 'undefined') {{
                var script = document.createElement('script');
                script.src = '{self.jquery_cdn_url}';
                script.onload = function() {{
                    console.log('jQuery berhasil dimuat dari CDN - Versi: ' + jQuery.fn.jquery);
                    window.jQueryLoaded = true;
                }};
                script.onerror = function(e) {{
                    console.error('Gagal memuat jQuery dari CDN:', e);
                    window.jQueryLoaded = false;
                }};
                document.head.appendChild(script);
            }} else {{
                console.log('jQuery sudah ada - Versi: ' + jQuery.fn.jquery);
                window.jQueryLoaded = true;
            }}
        }})();
        """
        self._run_javascript(web_object, script)
        self.periksa_jquery_dimuat(web_object)

    def periksa_jquery_dimuat(self, web_object):
        script = """
        (function() {
            if (typeof jQuery !== 'undefined') {
                console.log('jQuery terdeteksi - Versi: ' + jQuery.fn.jquery);
                return {loaded: true, version: jQuery.fn.jquery};
            } else {
                console.log('jQuery tidak terdeteksi');
                return {loaded: false, version: null};
            }
        })();
        """
        self._run_javascript(web_object, script, self.handle_jquery_check)

    def handle_jquery_check(self, result):
        if result is None:
            self.jquery_loaded = False
            self.jquery_version = None
            return
        
        self.jquery_loaded = result['loaded']
        self.jquery_version = result['version']
        if self.jquery_loaded:
            self.logger.info(f"jQuery terdeteksi - Versi: {self.jquery_version}")

    def pastikan_jquery_dimuat(self, web_object, timeout=1000):
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            self.periksa_jquery_dimuat(web_object)
            if self.jquery_loaded:
                return True
            time.sleep(0.1)
        self.logger.error(f"Timeout: jQuery tidak dimuat dalam {timeout} ms")
        return False

    def jalankan_jquery(self, web_object, script):
        if not self.jquery_loaded:
            self.logger.warning("jQuery belum dimuat. Mencoba memuat...")
            if not self.pastikan_jquery_dimuat(web_object):
                self.logger.error("Gagal memuat jQuery. Tidak dapat menjalankan script.")
                return

        full_script = f"jQuery(function() {{ {script} }});"
        self._run_javascript(web_object, full_script, self.handle_script_result)

    def handle_script_result(self, result):
        if result is not None:
            self.logger.info(f"Script jQuery berhasil dijalankan. Hasil: {result}")
        else:
            self.logger.info("Script jQuery selesai dijalankan tanpa hasil yang dikembalikan.")

    def _run_javascript(self, web_object, script, callback=None):
        if isinstance(web_object, QWebEngineView):
            if callback:
                web_object.page().runJavaScript(script, callback)
            else:
                web_object.page().runJavaScript(script)
        elif isinstance(web_object, QWebEnginePage):
            if callback:
                web_object.runJavaScript(script, callback)
            else:
                web_object.runJavaScript(script)
        else:
            raise TypeError("Objek harus berupa QWebEngineView atau QWebEnginePage")

    def tangani_konsol_javascript(self, level, message, line, source):
        level_str = {
            0: "INFO",
            1: "WARNING",
            2: "ERROR"
        }.get(level, "UNKNOWN")

        if 'jQuery' in message or 'jquery' in message.lower():
            self.logger.debug(f"jQuery Log [{level_str}]: {message} (baris {line} di {source})")
        
        if level == 2:
            self.logger.error(f"JavaScript Error: {message} (baris {line} di {source})")

    def reset(self):
        self.jquery_loaded = False
        self.jquery_version = None
        self.logger.info("Status jQuery direset")