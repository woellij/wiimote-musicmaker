import time
from PyQt5 import QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *

from src.pointer import PointerWheelEvent


class DrawHelper(object):
    @staticmethod
    def drawTriangle(qp, x, y, width, height):
        qp = qp # type: QPainter

        pointsCoord = [[x + width * 0.5,0], [x, height ], [x + width, height]]
        trianglePolygon = QPolygonF()
        for i in pointsCoord:
            trianglePolygon.append(QPointF(i[0], i[1]))

        qp.drawPolygon(trianglePolygon)

    @staticmethod
    def drawZig(qp, x, y, width, height):
        qp = qp # type: QPainter
        pointsCoord = [[x, y + height],[x + width * 0.33, y], [x + width * 0.66, y + height], [x + width, y]]
        trianglePolygon = QPolygonF()
        for i in pointsCoord:
            trianglePolygon.append(QPointF(i[0], i[1]))
        qp.drawPolygon(trianglePolygon)

    @staticmethod
    def drawBracket(qp, x,y,width,height):
        qp = qp # type: QPainter
        ps = [[x + width, y ],[x, y], [x , y + height], [x + width, y + height]]

        qp.drawLine(ps[0][0], ps[0][1], ps[1][0], ps[1][1])
        qp.drawLine(ps[1][0], ps[1][1], ps[2][0], ps[2][1])
        qp.drawLine(ps[2][0], ps[2][1], ps[3][0], ps[3][1])


class PlayWidget(QWidget):
    defaultVolume = 0.5

    def __init__(self, filename1, filename2, drawFunc = None):
        self.soundNum = 1
        super(PlayWidget, self).__init__()
        self.playStart = time.time()
        self.filename1 = filename1
        self.filename2 = filename2
        self.sound = QSoundEffect()
        self.drawFunc = drawFunc
        self.setSource(1)
        self.sound.playingChanged.connect(self.playingChanged)
        self.sound.setVolume(PlayWidget.defaultVolume)

    def playingChanged(self):
        self.update()


    def play(self):
        if(self.sound.isPlaying()):
            return
        now = time.time()
        if(now - self.playStart < 0.5):
            return

        self.playStart = now
        self.sound.play()

    def mouseReleaseEvent(self, ev):
        if ev.button() & Qt.ExtraButton3:
            self.setSource(1)
        elif ev.button() & Qt.ExtraButton4:
            self.setSource(2)

    def setSource(self, num):
        self.soundNum = num
        filename = self.filename1 if num == 1 else self.filename2
        self.sound.setSource(QUrl.fromLocalFile(filename))
        self.update()

    def wheelEvent(self, ev):
        QWidget.wheelEvent(self, ev)
        vol = self.sound.volume()
        if type(ev) is QWheelEvent:
            ev = ev # type:QWheelEvent
            a = ev.angleDelta()

            changeVol = 0.05
            vol = vol + changeVol if a.y() > 0 else vol - changeVol

        elif type(ev) is PointerWheelEvent:
            ev = ev # type:PointerWheelEvent
            dif = ev.pointerAngleDelta * 2
            dif = dif / 180
            dif = vol * dif
            vol += dif

        if vol > 0 and vol < 1.0:
            self.sound.setVolume(vol)
            self.update()

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
        self.paintIcon(p, (self.width() -width ) * 0.5, (self.height() -height) * 0.5, width-1, height-1)
        p.end()

    def paintIcon(self, qp, x,y,width, height):
        if(self.drawFunc):
            self.drawFunc([qp, x,y,width, height])
        pass

