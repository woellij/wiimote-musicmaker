
from PyQt5.QtWidgets import QDial, QWidget
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QUndoCommand

from drawWidget import QDrawWidget
from recognizer import Recognizer
from wiimotePointer import *
import template

from irMarker import IrMarkerEventFilter

class RelayUndoCommand(QUndoCommand):
    def __init__(self, redo, undo):
        super(RelayUndoCommand, self).__init__()
        self.__redo, self.__undo = redo, undo

    def undo(self):
        self.__undo()

    def redo(self):
        self.__redo()


class MusicMakerApp(QDrawWidget):
    def __init__(self, pointerEventCallback):
        super(MusicMakerApp, self).__init__(self.onComplete)

        self.markerHelper = IrMarkerEventFilter(self)
        self.installEventFilter(self.markerHelper)

        self.recognizer = Recognizer()
        self.recognizer.addTemplate(template.Template(template.circle[0], template.circle[1]))


    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)

        if self.markerHelper.markerMode:
            self.drawMarkers(qp)
        qp.end()
        QDrawWidget.paintEvent(self, ev)


    def drawMarkers(self, qp):
        for p in self.markerHelper.markers:
            # optionally fill each circle yellow
            qp.setBrush(Qt.red)
            qp.drawEllipse(p, 10, 10)


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