from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget


class PointerWidget(QWidget):
    def __init__(self, pointer):
        super(PointerWidget, self).__init__()

        self.pointer = pointer
        self.setFixedWidth(10)
        self.setFixedHeight(10)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, QPaintEvent):
        QWidget.paintEvent(self, QPaintEvent)
        qp = QPainter()
        qp.begin(self)

        qp.setBrush(self.pointer.color)
        qp.drawEllipse(0, 0, 10 - 1, 10 - 1)

        qp.end()

    def move(self, pos):
        # make new pos to center
        pos = QPoint(pos.x() - self.width() * 0.5, pos.y() - self.height() * 0.5)
        # make this always on top
        self.raise_()
        QWidget.move(self, pos)
