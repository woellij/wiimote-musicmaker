
from PyQt5 import QtWidgets, QtCore, QtGui


class QDrawWidget(QtWidgets.QWidget):

    def __init__(self, onCompleteCallback):
        super(QDrawWidget, self).__init__()
        self.onCompleteCallback = onCompleteCallback
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.points = []
        #QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(*self.start_pos)))
        self.setMouseTracking(True) # only get events when button is pressed
        self.initUI()

    def initUI(self):
        self.text = "Please click on the target"
        self.setWindowTitle('Drawable')
        self.show()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.points = []
            self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = False
            self.update()
            self.onCompleteCallback(self.points)

    def mouseMoveEvent(self, ev):
        if self.drawing:
            self.points.append((ev.x(), ev.y()))
            self.update()

    def poly(self, pts):
        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*p), pts))

    def drawPoints(self, points):
        self.points = points
        self.update()

    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(self.rect())
        qp.setBrush(QtGui.QColor(20, 255, 190))
        qp.setPen(QtGui.QColor(0, 155, 0))
        qp.drawPolyline(self.poly(self.points))
        for point in self.points:
            qp.drawEllipse(point[0]-1, point[1] - 1, 2, 2)
        qp.end()