from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication

from app import MusicMakerApp
from dragOperation import DragOperation
from pointer import PointerEvent


class DragEventFilter(QObject):
    def __init__(self, qapp):
        super(DragEventFilter, self).__init__()
        self.dragOperations = dict()
        self.qapp = qapp  # type: QApplication

    def eventFilter(self, obj, event):
        if not type(event) is PointerEvent:
            return False

        event = event  # type: PointerEvent
        pos = event.globalPos()

        if event.button() == QtCore.Qt.LeftButton:
            if event.type() == QMouseEvent.MouseButtonPress:

                widget = self.qapp.widgetAt(pos.x(), pos.y())
                if (not widget or widget is self.qapp or type(widget) == MusicMakerApp):
                    return False

                self.dragOperations[event.pointer] = DragOperation(widget, event)
                print("DragEventFilter handling mouse left button press")
                return True
            if event.type() == QMouseEvent.MouseButtonRelease:
                operation = self.dragOperations.get(event.pointer, None)
                if operation:
                    if (operation.changed):
                        event.pointer.undoStack().push(operation)
                    self.dragOperations.pop(event.pointer)
                    print("DragEventFilter handling mouse left button release")
                    return True

        if event.type() == QMouseEvent.MouseMove:
            operation = self.dragOperations.get(event.pointer, None)
            if operation:
                operation.apply(event)
                return False  # not handled so the pointer can update aswell. handing button down already prevents the widget itself from handling

        return False
