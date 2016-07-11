from PyQt5 import QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *

from pyo import *

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
        super(PlayWidget, self).__init__()
        self.filename1 = filename1
        self.filename2 = filename2
        self.sound = QSoundEffect()
        self.drawFunc = drawFunc
        self.sound.setSource(QUrl.fromLocalFile(filename1))

        self.sound.setVolume(PlayWidget.defaultVolume)

    def keyReleaseEvent(self, QKeyEvent):
        QWidget.keyReleaseEvent(self, QKeyEvent)
        print "keyrelease"

    def play(self):
        if(self.sound.isPlaying()):
            return
        self.sound.play()

    def wheelEvent(self, ev):
        QWidget.wheelEvent(self, ev)
        ev = ev # type:QWheelEvent
        a = ev.angleDelta()
        vol = self.sound.volume()

        changeVol = 0.05
        vol = vol + changeVol if a.y() > 0 else vol - changeVol
        print vol
        if vol > 0 and vol < 1.0:
            self.sound.setVolume(vol)
            self.update()

    def paintEvent(self, QPaintEvent):
        QWidget.paintEvent(self, QPaintEvent)
        p = QPainter()


        p.begin(self)

        p.setBrush(Qt.blue)
        pen = p.pen()
        pen.setWidth(5)
        pen.setColor(Qt.yellow)
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

