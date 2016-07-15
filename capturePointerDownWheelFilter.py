from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QMouseEvent

from app import MusicMakerApp
from pointer import PointerEvent, PointerWheelEvent


class WheelOperation(object):
    def __init__(self, widget, event):
        super(WheelOperation, self).__init__()
        self.changed = False

    def apply(self, event):
        print(event)


class CapturePointerWheelEventFilter(QObject):
    def __init__(self, qapp):
        super(CapturePointerWheelEventFilter, self).__init__()
        self.qapp = qapp
        self.operations = dict()

    def eventFilter(self, obj, event):
        if type(event) is PointerEvent:
            event = event  # type: PointerEvent
            pos = event.globalPos()

            if event.button() == QtCore.Qt.RightButton:
                if event.type() == QMouseEvent.MouseButtonPress:

                    widget = self.qapp.widgetAt(pos.x(), pos.y())
                    if (not widget or widget is self.qapp or type(widget) == MusicMakerApp):
                        return False

                    self.operations[event.pointer] = WheelOperation(widget, event)
                    return True
                if event.type() == QMouseEvent.MouseButtonRelease:
                    operation = self.operations.get(event.pointer, None)
                    if operation:
                        if (operation.changed):
                            event.pointer.undoStack().push(operation)
                        self.operations.pop(event.pointer)
                        return True

            elif event.type() == QMouseEvent.MouseMove:
                operation = self.operations.get(event.pointer, None)
                if operation:
                    # captured
                    return True

        elif type(event) is PointerWheelEvent:
            operation = self.operations.get(event.pointer, None)
            if operation:
                operation.apply(event)
                return False  # not handled so the pointer can update aswell. handling button down already prevents the widget itself from moving

        return False
