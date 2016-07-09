from PyQt5 import uic, QtWidgets
import numpy.random as random

import math
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QDial, QWidget
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QUndoCommand

from knob import Knob
from Sounds import SynthSound
from drawWidget import QDrawWidget
from recognizer import Recognizer
from wiimotePointer import *
import template

class RelayUndoCommand(QUndoCommand):
    def __init__(self, redo, undo):
        super(RelayUndoCommand, self).__init__()
        self.__redo, self.__undo = redo, undo

    def undo(self):
        self.__undo()

    def redo(self):
        self.__redo()

class IrMarkerHelper(QObject):

    markModifierKey = QtCore.Qt.Key_Control

    def __init__(self, widget):
        super(IrMarkerHelper, self).__init__()
        self.markers = WiiMotePositionMapper.markers
        self.widget = widget
        self.markerMode = False

    def eventFilter(self, obj, event):
        t = event.type()
        if(type(event) is QtGui.QKeyEvent):
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

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == IrMarkerHelper.markModifierKey:
            self.markerMode = True
            self.widget.setCursor(QCursor(QtCore.Qt.CrossCursor))
            self.widget.update()


    def addIrMarker(self, pos):
        if(len(self.markers) >= 4):
            distanceFunc = lambda p: math.hypot(p.x() - pos.x(), p.y() - pos.y())
            distances = map(lambda  p: (p, distanceFunc(p)), self.markers)
            print distances
            toRemove = min(distances, key= lambda tuple: tuple[1])
            self.markers.remove(toRemove[0])
        self.markers.append(pos)
        self.widget.update()

    def keyReleaseEvent(self, QKeyEvent):
        if QKeyEvent.key() == IrMarkerHelper.markModifierKey:
            self.markerMode=False
            self.widget.setCursor(QCursor(QtCore.Qt.BlankCursor))
            self.widget.update()


class MusicMakerApp(QDrawWidget):


    def __init__(self, pointerEventCallback):
        super(MusicMakerApp, self).__init__(self.onComplete)

        self.markerHelper = IrMarkerHelper(self)
        self.installEventFilter(self.markerHelper)

        self.recognizer = Recognizer()
        self.recognizer.addTemplate(template.Template(template.circle[0], template.circle[1]))

        self.setCursor(QCursor(QtCore.Qt.BlankCursor))


    def paintEvent(self, ev):
        QDrawWidget.paintEvent(self, ev)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        if self.markerHelper.markerMode:
            for p in self.markerHelper.markers:
                # optionally fill each circle yellow
                qp.setBrush(Qt.red)
                qp.drawEllipse(p, 10, 10)
        qp.end()


    def onComplete(self, points):
        if(len(points) <= 2):
            return

        recognized = self.recognizer.recognize(points)
        template =  recognized[0] # type: template.Template

        print(self.size())
        if(template):
            print template.name + " recognized"
            command = self.resolveCommand(template.name, points)
            # TODO recognize pointer and add it to that one's stack
            command.redo()

        else:
            # TODO output some status
            pass

    def resolveCommand(self, templateName, points):
        widget = None # type: QWidget
        if templateName == "circle":
            widget= QDial()

        if(not widget):
            return None

        self.setupChildWidget(widget, points)
        return RelayUndoCommand(lambda: widget.show(), lambda: widget.hide())

    def setupChildWidget(self, widget, points):
        widget.setFixedWidth(100)
        widget.setFixedHeight(100)

        x = sum(map(lambda t: t[0], points)) / len(points) - widget.width() * 0.5
        y = sum(map(lambda t: t[1], points)) / len(points) - widget.height() * 0.5
        widget.move(x, y)
        widget.setParent(self)