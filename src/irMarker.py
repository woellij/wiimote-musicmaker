import math
from PyQt5.QtCore import QObject
from PyQt5 import QtGui, QtCore
from wiimotePointer import *


class IrMarkerEventFilter(QObject):
    markModifierKey = QtCore.Qt.Key_Control

    def __init__(self, widget):
        super(IrMarkerEventFilter, self).__init__()
        self.markers = WiiMotePositionMapper.markers
        self.widget = widget
        self.widget.setCursor(QCursor(QtCore.Qt.BlankCursor))
        self.markerMode = False

    def eventFilter(self, obj, event):
        t = event.type()
        if (type(event) is QtGui.QKeyEvent):
            if t == QtGui.QKeyEvent.KeyPress:
                self.keyPressEvent(event)
            elif t == QtGui.QKeyEvent.KeyRelease:
                self.keyReleaseEvent(event)

            return True

        ev = event

        if t == QtGui.QKeyEvent.MouseButtonRelease or t == QtGui.QKeyEvent.MouseButtonPress:
            if ev.modifiers() & QtCore.Qt.ControlModifier:
                self.addIrMarker(ev.localPos())

                return True

        return False

    def  drawMarkers(self, qp):
        for p in self.markerHelper.markers:
            # optionally fill each circle yellow
            qp.setBrush(Qt.red)
            qp.drawEllipse(p, 10, 10)


    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == IrMarkerEventFilter.markModifierKey:
            self.markerMode = True
            self.widget.setCursor(QCursor(QtCore.Qt.CrossCursor))
            self.widget.update()

    def addIrMarker(self, pos):
        if (len(self.markers) >= 4):
            distanceFunc = lambda p: math.hypot(p.x() - pos.x(), p.y() - pos.y())
            distances = map(lambda p: (p, distanceFunc(p)), self.markers)
            print distances
            toRemove = min(distances, key=lambda tuple: tuple[1])
            self.markers.remove(toRemove[0])
        self.markers.append(pos)
        self.widget.update()

    def keyReleaseEvent(self, QKeyEvent):
        if QKeyEvent.key() == IrMarkerEventFilter.markModifierKey:
            self.markerMode = False
            self.widget.setCursor(QCursor(QtCore.Qt.BlankCursor))
            self.widget.update()
