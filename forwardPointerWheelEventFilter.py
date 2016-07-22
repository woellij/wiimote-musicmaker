from PyQt5.QtCore import QObject

from playWidget import PlayWidget
from pointer import PointerWheelEvent


class SendPointerEventToFirstPlayWidgetFilter(QObject):
    def __init__(self, qapp):
        super(SendPointerEventToFirstPlayWidgetFilter, self).__init__()
        self.qapp = qapp  # type: QApplication

    def eventFilter(self, obj, event):
        return False

        if type(event) is PointerWheelEvent:
            for w in self.qapp.allWidgets():
                if type(w) is PlayWidget:
                    w.event(event)
                    return True

        return False
