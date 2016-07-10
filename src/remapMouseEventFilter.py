from PyQt5 import QtCore, Qt

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from pointer import *


class RemapMouseEventFilter(QObject):

    def __init__(self, qapp, widget):
        super(RemapMouseEventFilter, self).__init__()
        self.qapp= qapp  # type: Qt.QApplication
        self.widget = widget # type: QWidget
        self.mousePointer = Pointer("mouse", QtCore.Qt.darkYellow)

    def eventFilter(self, obj, event):
        if(type(event) is QMouseEvent):
            pointerEvent = PointerEvent(self.mousePointer, event)
            self.qapp.sendEvent(obj, pointerEvent)
            return True

        return False