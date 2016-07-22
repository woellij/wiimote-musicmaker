
from PyQt5.QtCore import QEvent, QPoint
from PyQt5.QtCore import QObject
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QUndoStack


class PointerEvent(QMouseEvent):
    def __init__(self, pointer, QMouseEvent, target):
        super(PointerEvent, self).__init__(QMouseEvent)
        self.pointer = pointer
        self.target = target


class PointerWheelEvent(QEvent):
    def __init__(self, pointer, angle, qwheelEvent):
        super(PointerWheelEvent, self).__init__(QEvent.None_)
        self.qwheelEvent = qwheelEvent
        self.pointer = pointer
        self.pointerAngleDelta = angle


class Pointer(object):
    def __init__(self, id, color):
        super(Pointer, self).__init__()
        self.__id = id
        self.__undoStack = QUndoStack()
        self.color = color
        self.pos = QPoint(0,0)

    def undoStack(self):  # type: QUndoStack
        """

        :return: QUndoStack
        """

        return self.__undoStack

    def id(self):  # type: str
        return self.__id
