
from PyQt5.QtWidgets import QDial, QWidget
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QUndoCommand

from drawWidget import QDrawWidget, PointerDrawEventFilter
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


class MusicMakerApp(QWidget):
    def __init__(self, pointerEventCallback):
        super(MusicMakerApp, self).__init__()

        self.markerHelper = IrMarkerEventFilter(self)
        self.installEventFilter(self.markerHelper)

        self.pointerDrawFilter = PointerDrawEventFilter(self, self.onPointerDrawComplete)
        self.installEventFilter(self.pointerDrawFilter)

        self.recognizer = Recognizer()
        self.recognizer.addTemplate(template.Template(template.circle[0], template.circle[1]))

    def onPointerDrawComplete(self, pointer, points):
        if (len(points) <= 2):
            return

        points = map(lambda p: (p.x(), p.y()), points)
        recognized = self.recognizer.recognize(points)
        template = recognized[0]  # type: template.Template

        print(self.size())
        if (template):
            print template.name + " recognized"
            command = self.resolveCommand(template.name, points)
            # TODO recognize pointer and add it to that one's stack
            command.redo()

        else:
            # TODO output some status
            pass

    def paintEvent(self, ev):
        QWidget.paintEvent(self, ev)

        qp = QtGui.QPainter()
        qp.begin(self)

        if self.markerHelper.markerMode:
            self.markerHelper.drawMarkers(qp)
        self.pointerDrawFilter.drawPoints(qp)

        qp.end()


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