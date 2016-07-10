from PyQt5.QtCore import QObject
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, Qt

from app import MusicMakerApp
from wiimotePointer import PointerEvent

from pointerWidget import PointerWidget

class DragOperation(object):
    
    def __init__(self, widget, event):
        super(DragOperation, self).__init__()
        self.widget = widget # type: QWidget
        self.widgetStartPos = self.widget.pos()
        self.dragStartPos = self.__getEventPos__(event)

    def finalize(self, event):
        print "finalizing"

    def apply(self, event):
        eventPos = self.__getEventPos__(event)
        eventDiff = eventPos - self.dragStartPos
        self.widget.move(self.widgetStartPos + eventDiff)
        print eventDiff

    def __getEventPos__(self, event):
        return event.globalPos()

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
                    operation.finalize(event)
                    self.dragOperations.pop(event.pointer)
                    return True



        if event.type() == QMouseEvent.MouseMove:
            operation = self.dragOperations.get(event.pointer, None)
            if operation:
                operation.apply(event)
                return False


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
