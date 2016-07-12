from PyQt5.QtCore import QObject
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, Qt

from PyQt5.QtWidgets import QUndoCommand

from app import MusicMakerApp
from wiimotePointer import *

from pointerWidget import PointerWidget

class DragOperation(QUndoCommand):
    """
    Class representing a drag operation on a widget.
    Adjusting the position through the apply method.
    """
    
    def __init__(self, widget, event):
        super(DragOperation, self).__init__()
        self.widget = widget # type: QWidget
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
        if(self.undone):
            self.widget.move(self.widget.pos() + self.latestEventDiff)
        else:
            self.widget.move(self.latestDragPosition)


class DragEventFilter(QObject):

    def __init__(self, qapp):
        super(DragEventFilter, self).__init__()
        self.dragOperations = dict()
        self.qapp = qapp # type: QApplication

    def eventFilter(self, obj, event):
        if not type(event) is PointerEvent:
            return False

        event = event # type: PointerEvent
        pos = event.globalPos()

        if event.button() == QtCore.Qt.LeftButton:
            if event.type() == QMouseEvent.MouseButtonPress:

                widget = self.qapp.widgetAt(pos.x(), pos.y())
                if (not widget or widget is self.qapp or type(widget) == MusicMakerApp):
                    return False

                self.dragOperations[event.pointer] = DragOperation(widget, event)
                return True
            if event.type() == QMouseEvent.MouseButtonRelease:
                operation = self.dragOperations.get(event.pointer, None)
                if operation:
                    if(operation.changed):
                        event.pointer.undoStack().push(operation)
                    self.dragOperations.pop(event.pointer)
                    return True

        if event.type() == QMouseEvent.MouseMove:
            operation = self.dragOperations.get(event.pointer, None)
            if operation:
                operation.apply(event)
                return False # not handled so the pointer can update aswell. handing button down already prevents the widget itself from handling

        return False

class WheelOperation(object):
    def __init__(self, widget, event):
        super(WheelOperation, self).__init__()
        self.changed = False


    def apply(self, event):
        print event


class PointerDownCaptureWheelFilter(QObject):

    def __init__(self, qapp):
        super(PointerDownCaptureWheelFilter, self).__init__()
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

        elif type(event) is PointerWheelEvent:
            operation = self.operations.get(event.pointer, None)
            if operation:
                operation.apply(event)
                return False  # not handled so the pointer can update aswell. handing button down already prevents the widget itself from handling

        return False

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
