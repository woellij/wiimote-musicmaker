import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *

from pointer import PointerWheelEvent


class PlayWidget(QWidget):
    defaultVolume = 0.5

    def __init__(self, filename1, filename2, drawFunc=None):
        self.soundNum = 1
        super(PlayWidget, self).__init__()
        self.playStart = time.time()
        self.filename1 = filename1
        self.filename2 = filename2
        self.sound = QSoundEffect()
        self.drawFunc = drawFunc
        self.setSource(1)
        self.setMouseTracking(False)
        self.sound.playingChanged.connect(self.playingChanged)
        self.sound.setVolume(PlayWidget.defaultVolume)

    def playingChanged(self):
        self.update()

    def play(self):
        if (self.sound.isPlaying()):
            return
        now = time.time()
        if (now - self.playStart < 0.5):
            return

        self.playStart = now
        self.sound.play()

    def mouseReleaseEvent(self, ev):
        print("received pointer button release event")
        if ev.button() & Qt.ExtraButton3:
            self.setSource(1)
        elif ev.button() & Qt.ExtraButton4:
            self.setSource(2)

    def setSource(self, num):
        self.soundNum = num
        filename = self.filename1 if num == 1 else self.filename2
        self.sound.setSource(QUrl.fromLocalFile(filename))
        self.update()

    def adjustVolume(self, angle):

        vol = self.sound.volume()
        dif = angle / 180
        dif = vol * dif
        vol += dif
        print("volume dif ", angle, dif)

        if vol > 0 and vol < 1.0:
            self.sound.setVolume(vol)
            self.update()

    def wheelEvent(self, ev):
        angle = ev.angleDelta().y() / 8
        self.adjustVolume(angle)

    def paintEvent(self, QPaintEvent):
        QWidget.paintEvent(self, QPaintEvent)
        p = QPainter()

        p.begin(self)
        p.setBrush(Qt.transparent)
        pen = p.pen()
        pen.setWidth(5)
        penc = Qt.magenta if self.sound.isPlaying() else Qt.blue if self.soundNum == 1 else Qt.darkBlue
        pen.setColor(penc)
        p.setPen(pen)

        width, height = self.width(), self.height()
        fac = self.sound.volume()
        width, height = width * fac, height * fac
        self.paintIcon(p, (self.width() - width) * 0.5, (self.height() - height) * 0.5, width - 1, height - 1)
        p.end()

    def paintIcon(self, qp, x, y, width, height):
        if (self.drawFunc):
            self.drawFunc([qp, x, y, width, height])
        pass
