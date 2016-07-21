from PyQt5 import QtCore, Qt
from PyQt5.QtCore import QObject, QPoint

from pointer import *


class RemapMouseEventFilter(QObject):
    def __init__(self, qapp, colorPick):
        super(RemapMouseEventFilter, self).__init__()
        self.colorPick = colorPick
        self.qapp = qapp  # type: Qt.QApplication
        self.mousePointer = Pointer("mouse", colorPick.pick())
        self.wheelevents = []

    def eventFilter(self, obj, event):

        if (type(event) is QKeyEvent):
            key = event.key()
            button = None
            if key == QtCore.Qt.Key_1:
                button = QtCore.Qt.ExtraButton3
            if key == QtCore.Qt.Key_2:
                button = QtCore.Qt.ExtraButton4
            if key == QtCore.Qt.Key_Backspace:
                button = QtCore.Qt.BackButton
            if key == QtCore.Qt.Key_Insert:
                button = QtCore.Qt.ForwardButton
            if button:
                t = QMouseEvent.MouseButtonRelease if event.type() == QKeyEvent.KeyRelease else QMouseEvent.MouseButtonPress
                pos = QPoint(self.latestMousePos[0], self.latestMousePos[1])
                target = self.qapp.widgetAt(pos)
                if (target):
                    localPos = target.mapFromGlobal(pos)
                    ev = QMouseEvent(t, localPos, pos, button, self.qapp.mouseButtons(), self.qapp.keyboardModifiers())
                    self.qapp.postEvent(target, PointerEvent(self.mousePointer, ev))
                    return True

        if (type(event) is QMouseEvent):
            ev = event # type: QMouseEvent
            self.latestMousePos = (event.globalPos().x(), event.globalPos().y())
            """ print("mouse move: %1 ",
                  ev.localPos(),
                  ev.windowPos(),
                  ev.screenPos(),
                  ev.globalPos())"""
            self.qapp.postEvent(obj, PointerEvent(self.mousePointer, event))
            return True

        return False
