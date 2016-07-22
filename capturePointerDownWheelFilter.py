from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QUndoCommand

from app import MusicMakerApp
from pointer import PointerEvent, PointerWheelEvent

class VolumeOperation(object):

    def __init__(self, widget):
        super(VolumeOperation, self).__init__()
        self.widget = widget

    def apply(self, event):
        self.widget.adjustVolume(event.pointerAngleDelta * 8)
        return True

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

                    self.operations[event.pointer] = VolumeOperation(widget)
                    return True
                if event.type() == QMouseEvent.MouseButtonRelease:
                    operation = self.operations.get(event.pointer, None)
                    if operation:
                        self.operations.pop(event.pointer)
                        print("capture done")
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
                return  True

        return False
