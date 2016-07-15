from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QMouseEvent

from pointer import PointerEvent


class PointerUndoRedoEventFilter(QObject):
    def eventFilter(self, obj, event):
        if not type(event) is PointerEvent:
            return False

        if event.type() == QMouseEvent.MouseButtonRelease:
            pointer = event.pointer  # type: Pointer
            if event.button() & QtCore.Qt.BackButton:
                if (pointer.undoStack().canUndo()):
                    pointer.undoStack().undo()
                    return True
            if event.button() & QtCore.Qt.ForwardButton:
                if (pointer.undoStack().canRedo()):
                    pointer.undoStack().redo()
                    return True

        return False
