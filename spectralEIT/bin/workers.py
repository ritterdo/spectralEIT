from sys import exc_info
# from traceback import format_exc,print_exc
from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal

class WorkerSignals(QObject):

    finished = pyqtSignal()
    result = pyqtSignal(str)
    progress = pyqtSignal(str,int)
    error = pyqtSignal(tuple,str)
    cancelled = pyqtSignal(str)

class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs["progress_callback"] = self.signals.progress


    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.fn(*self.args, **self.kwargs)
        except InterruptedError:
            self.signals.cancelled.emit(self.kwargs["objectName"])
        except Exception:
            self.signals.error.emit(exc_info(), self.kwargs["objectName"])
        else:
            self.signals.result.emit(self.kwargs["objectName"])  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
