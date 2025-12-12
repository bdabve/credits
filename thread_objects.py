# Server for api
from threading import Thread
import uvicorn
from api import app as server_app
from PyQt5 import QtCore


class ServerThread(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        config = uvicorn.Config(server_app, host="127.0.0.1", port=8000, log_level="info")
        self.server = uvicorn.Server(config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


class DriverGraphWorker(QtCore.QThread):
    finished = QtCore.pyqtSignal(object, object, object)  # df, sum_retour, error

    def __init__(self, file_path, month="DECEMBRE"):
        super().__init__()
        self.file_path = file_path
        self.month = month

    def run(self):
        try:
            import etat_statistics as st

            # 1) Load Excel (HEAVY)
            df = st.load_excel(self.file_path, self.month)

            # 2) Compute retour
            les_retour, sum_retour = st.driver_retour(df)

            self.finished.emit(df, sum_retour, None)

        except Exception as e:
            self.finished.emit(None, None, str(e))


class PlotWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(object)   # will emit df when done
    error = QtCore.pyqtSignal(str)

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path

    def run(self):
        import etat_statistics as st  # your module
        try:
            df = st.load_excel(self.file_path, "DECEMBRE")
            self.finished.emit(df)
        except Exception as e:
            self.error.emit(str(e))
