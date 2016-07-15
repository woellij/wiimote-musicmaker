from PyQt5.QtGui import *
from PyQt5.QtWidgets import QUndoStack


class PointerEvent(QMouseEvent):
    def __init__(self, pointer, QMouseEvent):
        super(PointerEvent, self).__init__(QMouseEvent)
        self.pointer = pointer


class PointerWheelEvent(QWheelEvent):
    def __init__(self, pointer, angle, qwheelevent):
        super(PointerWheelEvent, self).__init__(qwheelevent)
        self.pointer = pointer
        self.pointerAngleDelta = angle


class Pointer(object):
    def __init__(self, id, color):
        super(Pointer, self).__init__()
        self.__id = id
        self.__undoStack = QUndoStack()
        self.color = color

    def undoStack(self):  # type: QUndoStack
        """

        :return: QUndoStack
        """

        return self.__undoStack

    def id(self):  # type: str
        return self.__id
