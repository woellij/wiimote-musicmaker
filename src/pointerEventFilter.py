from PyQt5.QtCore import QObject
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, Qt

from PyQt5.QtWidgets import QUndoCommand

from src.app import MusicMakerApp
from src.wiimotePointer import *

from src.pointerWidget import PointerWidget


class PointerUndoRedoEventFilter(QObject):

    def eventFilter(self, obj, event):
        if not type(event) is PointerEvent:
            return False

        if event.type() == QMouseEvent.MouseButtonRelease:
            pointer = event.pointer # type: Pointer
            if event.button() & QtCore.Qt.BackButton:
                if(pointer.undoStack().canUndo()):
                    pointer.undoStack().undo()
                    return True
            if event.button() & QtCore.Qt.ForwardButton:
                if(pointer.undoStack().canRedo()):
                    pointer.undoStack().redo()
                    return True

        return False


class PointerEventFilter(QObject):
    def __init__(self, widget, qapp):
        super(PointerEventFilter, self).__init__()

        self.qapp = qapp # type: Qt.QApplication
        self.widget = widget # type: QWidget
        self.__pointers = dict()

    def pointers(self):
        return self.__pointers.values()

    def eventFilter(self, obj, event):
        if not type(event) is PointerEvent:
            return False

        ev = event # type: PointerEvent
        t = ev.type()

        if t == QMouseEvent.MouseMove:
            self.getPointerWidget(event).move(ev.windowPos())
        return False

    def getPointerWidget(self, ev):
        id = ev.pointer.id()
        pointerWidget = self.__pointers.get(id, None)
        if not pointerWidget:
            pointerWidget = PointerWidget(self.widget, ev.pointer)
            self.__pointers[id] = pointerWidget
            pointerWidget.show()
        return pointerWidget
