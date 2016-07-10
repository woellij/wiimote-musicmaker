from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Playhead(QWidget):
    def __init__(self, parent, callback):
        super(Playhead, self).__init__(parent)
        self.t = self.startTimer(5)
        self.width = 5
        self.stepping = self.width
        self.callback = callback

    def timerEvent(self, t):

        self.xpos = self.pos().x() + self.stepping
        if self.xpos + self.width > self.parent().width():
            self.xpos = 0
        self.move(self.xpos, 0)
        self.callback(self.xpos, self.stepping)

    def paintEvent(self, QPaintEvent):
        self.setFixedHeight(self.parent().height())
        QWidget.paintEvent(self, QPaintEvent)
        p = QPainter()
        p.begin(self)
        p.setBrush(Qt.red)
        p.drawRect(0,0, self.width, self.height())
