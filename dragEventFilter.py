from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QUndoCommand
from app import MusicMakerApp

from pointer import PointerEvent


class DragOperation(QUndoCommand):
    """
    Class representing a drag operation on a widget.
    Adjusting the position through the apply method.
    """

    def __init__(self, widget, event):
        super(DragOperation, self).__init__()
        self.widget = widget  # type: QWidget
        self.widgetStartPos = self.widget.pos()
        self.dragStartPos = self.__getEventPos__(event)
        self.undone = False
        self.changed = False

    def apply(self, event):
        self.changed = True
        eventPos = self.__getEventPos__(event)
        self.latestEventDiff = eventDiff = eventPos - self.dragStartPos
        self.latestDragPosition = self.widgetStartPos + eventDiff
        self.widget.move(self.latestDragPosition)

    def __getEventPos__(self, event):
        return event.globalPos()

    def undo(self):
        self.undone = True
        self.widget.move(self.widgetStartPos)

    def redo(self):
        if not hasattr(self, "latestDragPosition"):
            return
        if (self.undone):
            self.widget.move(self.widget.pos() + self.latestEventDiff)
        else:
            self.widget.move(self.latestDragPosition)


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