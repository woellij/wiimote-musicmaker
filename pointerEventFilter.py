from PyQt5 import Qt

from oneEuroFilter import OneEuroFilter
from pointerWidget import PointerWidget
from wiimotePointer import *


class PointerEventFilter(QObject):
    def __init__(self, widget, qapp):
        super(PointerEventFilter, self).__init__()

        self.qapp = qapp  # type: Qt.QApplication
        self.widget = widget  # type: QWidget
        self.__pointers = dict()

    def pointers(self):
        return self.__pointers.values()

    def eventFilter(self, obj, event):
        if not type(event) is PointerEvent:
            return False

        ev = event  # type: PointerEvent
        t = ev.type()

        if t == QMouseEvent.MouseMove:
            pos = ev.globalPos()
            widgetPos = pos - self.qapp.topLevelWidgets()[0].mapToGlobal(QPoint(0, 0))
            self.getPointerWidget(event).move(widgetPos)
        return False


    def getPointerWidget(self, ev):
        id = ev.pointer.id()
        pointerWidget = self.__pointers.get(id, None)
        if not pointerWidget:
            pointerWidget = PointerWidget(ev.pointer)
            pointerWidget.moveToThread(QApplication.instance().thread())
            pointerWidget.setParent(self.widget)
            self.__pointers[id] = pointerWidget
            pointerWidget.show()
        return pointerWidget
