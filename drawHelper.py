from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPolygonF


class DrawHelper(object):
    @staticmethod
    def drawTriangle(qp, x, y, width, height):
        qp = qp  # type: QPainter

        pointsCoord = [[x + width * 0.5, 0], [x, height], [x + width, height]]
        trianglePolygon = QPolygonF()
        for i in pointsCoord:
            trianglePolygon.append(QPointF(i[0], i[1]))

        qp.drawPolygon(trianglePolygon)

    @staticmethod
    def drawZig(qp, x, y, width, height):
        qp = qp  # type: QPainter
        pointsCoord = [[x, y + height], [x + width * 0.33, y], [x + width * 0.66, y + height], [x + width, y]]
        trianglePolygon = QPolygonF()
        for i in pointsCoord:
            trianglePolygon.append(QPointF(i[0], i[1]))
        qp.drawPolygon(trianglePolygon)

    @staticmethod
    def drawBracket(qp, x, y, width, height):
        qp = qp  # type: QPainter
        ps = [[x + width, y], [x, y], [x, y + height], [x + width, y + height]]

        qp.drawLine(ps[0][0], ps[0][1], ps[1][0], ps[1][1])
        qp.drawLine(ps[1][0], ps[1][1], ps[2][0], ps[2][1])
        qp.drawLine(ps[2][0], ps[2][1], ps[3][0], ps[3][1])
