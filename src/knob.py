from PyQt5 import QtWidgets

from PyQt5.QtGui import *
import PyQt5.QtCore as QtCore
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import QWidget

from pyo import *


class PlayWidget(QWidget):
    def __init__(self, filename):
        super(PlayWidget, self).__init__()
        self.filename = filename
        self.sound = QSound(filename, self)


    def play(self):
        if(not self.sound.isFinished()):
            return
        self.sound.play()

    def paintEvent(self, QPaintEvent):
        QWidget.paintEvent(self, QPaintEvent)
        p = QPainter()
        p.begin(self)
        p.setBrush(QtCore.Qt.blue)
        p.drawEllipse(0,0, self.width()-1, self.height()-1)
        p.end()





