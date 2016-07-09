from PyQt5.QtCore import QObject
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, Qt
from wiimotePointer import PointerEvent

from pointerWidget import PointerWidget


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

        widgetUnderPointer = self.qapp.widgetAt(ev.pos())  # type: QWidget

        if (widgetUnderPointer and not widgetUnderPointer is obj):
            localPos = widgetUnderPointer.mapFromGlobal(ev.globalPos())

            localEvent = QMouseEvent(ev.type(), localPos, ev.globalPos(), ev.button(), ev.buttons(), ev.modifiers())
            localPointerEvent = PointerEvent(ev.pointer, localEvent)
            self.qapp.sendEvent(widgetUnderPointer, localPointerEvent)
            # widgetUnderPointer.event(localPointerEvent)

        if t == QMouseEvent.MouseMove:
            self.getPointerWidget(event).move(ev.pos())

        return False

    def getPointerWidget(self, ev):
        id = ev.pointer.id()
        pointerWidget = self.__pointers.get(id, None)
        if not pointerWidget:
            pointerWidget = PointerWidget(self.widget, ev.pointer)
            self.__pointers[id] = pointerWidget
            pointerWidget.show()
        return pointerWidget
