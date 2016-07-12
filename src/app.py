
from PyQt5.QtWidgets import QDial, QWidget
from PyQt5 import *

import os.path

from PyQt5.QtWidgets import QLayout
from PyQt5.QtWidgets import QUndoCommand

from drawWidget import QDrawWidget, PointerDrawEventFilter
from recognizer import Recognizer
from playWidget import *
from wiimotePointer import *
from playhead import Playhead
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

    def __init__(self, parent, widget, inverted = False):
        super(DeleteCommand, self).__init__()
        self.widget = widget # type: QWidget
        self.parent = parent
        self.inverted = inverted

    def undo(self):
        if(self.inverted):
            self._hide()
            return
        self._show()

    def redo(self):
        if(self.inverted):
            self._show()
            return
        self._hide()

    def _hide(self):
        self.widget.setParent(None)
        self.widget.hide()

    def _show(self):
        self.widget.setParent(self.parent)
        self.widget.show()

class AddCommand(DeleteCommand):
    def __init__(self, parent, widget, inverted=False):
        super(AddCommand, self).__init__(parent, widget, True)

class RecThread(QThread):

    finished = pyqtSignal(object)

    def __init__(self, recognizer, points, pointer):
        super(RecThread, self).__init__()
        self.pointer = pointer
        self.recognizer, self.points = recognizer, points
        self.res = None

    def run(self):
        self.res = self.recognizer.recognize(self.points)
        self.finished.emit(self)

class MusicMakerApp(QWidget):

    TEMPLATEWIDGETFACTORIES = {
        "circle": lambda: PlayWidget("../samples/clap.wav", "../samples/cymbal.wav", lambda args: args[0].drawEllipse(*args[1:])),
        "rectangle": lambda: PlayWidget("../samples/kick.wav","../samples/rs.wav", lambda args: args[0].drawRect(*args[1:])),
        "caret": lambda: PlayWidget("../samples/hh.wav","../samples/ohh.wav", lambda args: DrawHelper.drawTriangle(*args)),
        "zig-zag": lambda: PlayWidget("../samples/sd1.wav", "../samples/sd2.wav", lambda args: DrawHelper.drawZig(*args)),
        "left_square_bracket": lambda: PlayWidget("../samples/cb.wav", "../samples/hc.wav", lambda args: DrawHelper.drawBracket(*args)),
    }

    def __init__(self):
        super(MusicMakerApp, self).__init__()
        self.setMinimumHeight(500)
        self.setMinimumWidth(800)

        self.pointerDrawFilter = PointerDrawEventFilter(self, self.onPointerDrawComplete)
        self.installEventFilter(self.pointerDrawFilter)

        self.markerHelper = IrMarkerEventFilter(self)
        self.installEventFilter(self.markerHelper)

        self.recognizer = Recognizer()
        self.recognizer.addTemplate(template.Template(*template.circle))
        self.recognizer.addTemplate(template.Template(*template.delete))
        self.recognizer.addTemplate(template.Template(*template.rectangle))
        self.recognizer.addTemplate(template.Template(*template.caret))
        self.recognizer.addTemplate(template.Template(*template.zig_zag))
        self.recognizer.addTemplate(template.Template(*template.left_square_bracket))

        self.threads = []
        self.head = Playhead(self, self.playheadMoved)

    def playheadMoved(self, xpos, stepping):
        cs = self.children()
        lower = xpos - stepping
        p = cs[0].pos().x()
        for c in cs:
            c = c # type: QWidget
            r = c.geometry() # type: QRect
            if c.isVisible() and (lower < r.x() < xpos) or (lower < r.right() < xpos):
                if hasattr(c, "play"):
                    c.play()

    def adjustSize(self):
        QWidget.adjustSize(self)
        self.head.adjustSize()

    def recognized(self, thread):
        print "recognized"
        self.threads.remove(thread)

        recognized = thread.res
        if not recognized:
            return

        pointer = thread.pointer
        points = thread.points

        template = recognized[0]  # type: template.Template
        if (template):
            if (recognized[1] > 0.5):
                print template.name + " recognized: " + str(recognized[1])
                command = self.resolveCommand(template.name, points)
                if (command):
                    pointer.undoStack().push(command)
            else:
                # TODO output some status
                pass


    def onPointerDrawComplete(self, pointer, points):
        if (len(points) <= 2):
            return

        points = map(lambda p: (p.x(), p.y()), points)
        thread = RecThread(self.recognizer, points, pointer)
        thread.finished.connect(self.recognized)
        thread.start()
        self.threads.append(thread)


    def paintEvent(self, ev):
        QWidget.paintEvent(self, ev)

        qp = QPainter()
        qp.begin(self)

        qp.setBrush(Qt.black)
        qp.drawRect(self.rect())

        if self.markerHelper.markerMode:
            self.markerHelper.drawMarkers(qp)
        self.pointerDrawFilter.drawPoints(qp)
        self.drawStepping(qp, self.head.stepping)

        qp.end()

    def drawStepping(self, qp, stepping):
        pos = 0
        qp.setBrush(Qt.yellow)
        pen = QPen()
        pen.setColor(Qt.darkGray)
        qp.setPen(pen)
        while pos < self.width():
            pos += stepping
            qp.drawLine(pos, 0, pos, self.height())


    def resolveCommand(self, templateName, points):

        if templateName == "delete":
            x, y = np.mean(points, 0)
            widget = self.childAt(x,y)
            if widget and not widget is self:
                return DeleteCommand(self, widget)

        widgetFactory = MusicMakerApp.TEMPLATEWIDGETFACTORIES.get(templateName, None)

        if(not widgetFactory):
            return None

        widget = widgetFactory()

        self.setupChildWidget(widget, points)
        return AddCommand(self, widget)

    def setupChildWidget(self, widget, points):
        widget.setFixedWidth(50)
        widget.setFixedHeight(50)

        x, y = np.mean(points,0 )
        x = x - widget.width() * 0.5
        y = y - widget.height() * 0.5
        widget.move(x, y)
        widget.setParent(self)
