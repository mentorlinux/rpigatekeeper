from django.apps import AppConfig
import threading
from .qr_scanner_thread import scan_qr_code_stream

class QrScannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qr_scanner'

    def ready(self):
        # Start the scanner in a background thread
        threading.Thread(target=scan_qr_code_stream, daemon=True).start()
