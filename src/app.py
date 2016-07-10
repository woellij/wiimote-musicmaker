
from PyQt5.QtWidgets import QDial, QWidget
from PyQt5 import QtGui, QtCore

from PyQt5.QtWidgets import QLayout
from PyQt5.QtWidgets import QUndoCommand

from drawWidget import QDrawWidget, PointerDrawEventFilter
from recognizer import Recognizer
from wiimotePointer import *
import template

import numpy as np

from irMarker import IrMarkerEventFilter

class RelayUndoCommand(QUndoCommand):
    def __init__(self, redo, undo):
        super(RelayUndoCommand, self).__init__()
        self.__redo, self.__undo = redo, undo

    def undo(self):
        self.__undo()

    def redo(self):
        self.__redo()

class DeleteCommand(QUndoCommand):

    def __init__(self, parent, widget):
        super(DeleteCommand, self).__init__()
        self.widget = widget # type: QWidget
        self.parent = parent

    def undo(self):
        self.widget.setParent(self.parent)
        self.widget.show()

    def redo(self):
        self.widget.setParent(None)
        self.widget.hide()

class MusicMakerApp(QWidget):
    def __init__(self):
        super(MusicMakerApp, self).__init__()

        self.pointerDrawFilter = PointerDrawEventFilter(self, self.onPointerDrawComplete)
        self.installEventFilter(self.pointerDrawFilter)

        self.markerHelper = IrMarkerEventFilter(self)
        self.installEventFilter(self.markerHelper)

        self.recognizer = Recognizer()
        self.recognizer.addTemplate(template.Template(template.circle[0], template.circle[1]))
        self.recognizer.addTemplate(template.Template(template.delete[0], template.delete[1]))

    def onPointerDrawComplete(self, pointer, points):
        if (len(points) <= 2):
            return

        points = map(lambda p: (p.x(), p.y()), points)
        recognized = self.recognizer.recognize(points)

        template = recognized[0]  # type: template.Template

        if (template):
            if(recognized[1] > 0.5):
                print template.name + " recognized: " + str(recognized[1])
                command = self.resolveCommand(template.name, points)
                if(command):
                    pointer.undoStack().push(command)
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

        if templateName == "delete":
            x, y = np.mean(points, 0)
            widget = self.childAt(x,y)
            if widget and not widget is self:
                return DeleteCommand(self, widget)


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

        x, y = np.mean(points,0 )
        x = x - widget.width() * 0.5
        y = y - widget.height() * 0.5
        widget.move(x, y)
        widget.setParent(self)
