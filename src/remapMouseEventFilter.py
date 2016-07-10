from PyQt5 import QtCore, Qt

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from pointer import *



class RemapMouseEventFilter(QObject):

    def __init__(self, qapp):
        super(RemapMouseEventFilter, self).__init__()
        self.qapp= qapp  # type: Qt.QApplication
        self.mousePointer = Pointer("mouse", QtCore.Qt.green)

    def eventFilter(self, obj, event):
        if(type(event) is QMouseEvent):
            self.qapp.sendEvent(obj, PointerEvent(self.mousePointer, event))
            return True

        return False