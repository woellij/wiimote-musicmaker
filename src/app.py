from PyQt5 import uic, QtWidgets
import numpy.random as random

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


class MusicMakerApp(QDrawWidget):
    def __init__(self, pointerEventCallback):
        super(MusicMakerApp, self).__init__(self.onComplete)

        self.recognizer = Recognizer()
        self.recognizer.addTemplate(template.Template(template.circle[0], template.circle[1]))

        self.pointerReceiver = WiiMotePointerReceiver(lambda: WiiMotePointerConfig(WiiMotePositionMapper(),
                                                                                   pointerEventCallback))
        self.pointerReceiver.start()


    def onComplete(self, points):
        if(len(points) <= 2):
            return

        recognized = self.recognizer.recognize(points)
        template =  recognized[0] # type: template.Template

        print(self.size())
        if(template):
            print template.name + " recognized"
            command = self.resolveCommand(template.name, points)

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
        widget.setParent(self),