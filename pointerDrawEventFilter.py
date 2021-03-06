from PyQt5.QtCore import QPoint
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication

from pointer import PointerEvent


class PointerDrawEventFilter(QObject):
    def __init__(self, widget, completeCallback):
        super(PointerDrawEventFilter, self).__init__()
        self.widget = widget
        self.completeCallback = completeCallback
        self.pointerPoints = dict()

    def setCompleteCallback(self, completeCallback):
        self.completeCallback = completeCallback

    def eventFilter(self, obj, event):

        if not type(event) is PointerEvent:
            return False
        t = event.type()

        if t == QtGui.QKeyEvent.MouseButtonRelease and event.button() & QtCore.Qt.LeftButton:
            return self.mouseReleaseEvent(event)
        elif t == QtGui.QMouseEvent.MouseMove and event.buttons() & QtCore.Qt.LeftButton:
            return self.pressedLeftButtonMouseMoveEvent(event)
        return False

    def pressedLeftButtonMouseMoveEvent(self, ev):
        points = self.pointerPoints.get(ev.pointer, None)
        if not points:
            self.pointerPoints[ev.pointer] = points = []
        points.append(ev.pointer.pos)
        return False

    def clearPointsFromPointer(self, pointer):
        try:
            self.pointerPoints.pop(pointer)
            self.widget.update()
        except:
            pass

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.widget.update()
            self.completeCallback(ev.pointer, self.pointerPoints.get(ev.pointer, []))
            self.clearPointsFromPointer(ev.pointer)
            return False
        return False

    def poly(self, pts):
        return QtGui.QPolygonF(pts)

    def drawPoints(self, qp):
        for pointer, points in self.pointerPoints.items():
            if points and len(points) > 0:
                qp.setBrush(pointer.color)
                qp.setPen(pointer.color)
                qp.drawPolyline(self.poly(points))

                for point in points:
                    qp.drawEllipse(point.x() - 1, point.y() - 1, 2, 2)
