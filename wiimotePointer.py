from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget

import wiimote
from pointer import *
from turnOperation import TurnOperation
from wiimotePositionMapper import WiiMotePositionMapper


class WiiMotePointer(Pointer):
    BUTTONMAP = {'A': Qt.RightButton,
                 'B': Qt.LeftButton,
                 'Home': Qt.MiddleButton,
                 'Minus': Qt.BackButton,
                 'One': Qt.ExtraButton3,
                 'Plus': Qt.ForwardButton,
                 'Two': Qt.ExtraButton4,
                 # 'Down': Qt.Key_Down,
                 # 'Left': Qt.Key_Left,
                 # 'Right': Qt.Key_Right,
                 # 'Up': Qt.Key_Up,
                 }

    def __init__(self, wiimote, qapp, color):
        super(WiiMotePointer, self).__init__(wiimote.btaddr, color)

        self.positionMapper = WiiMotePositionMapper()
        self.qapp = qapp  # type: QApplication
        self.point = QPoint(0, 0)
        self.turnOperation = None

        self.wm = wiimote  # type: wiimote.WiiMote
        self.wm.buttons.register_callback(self.__onButtonEvent__)
        self.wm.accelerometer.register_callback(self.__onAccelerometerData__)
        self.wm.ir.register_callback(self.__onIrData__)

    def __onAccelerometerData__(self, data):
        if self.turnOperation:
            angle = self.turnOperation.getAngle(data)
            if angle:
                self.__sendWheelEvent__(angle)

    def __sendWheelEvent__(self, angle):
        targetWidget, localPos = self.__getLocalEventProperties__()

        wheelEv = QWheelEvent(localPos, self.point, QPoint(0, 0), QPoint(0, angle), abs(angle), Qt.Vertical,
                              self.__mapActiveMouseButtons__(), self.qapp.keyboardModifiers())
        ev = PointerWheelEvent(self, angle, wheelEv)

        self.qapp.postEvent(targetWidget, ev)

    def __onIrData__(self, data):
        p = self.positionMapper.map(data)
        if not p:
            return
        x, y = p[0], p[1]

        point = QPoint(x, y)
        changed = not self.point == point
        self.point = QPoint(x, y)
        if (changed):
            self.__sendEvent__(QEvent.MouseMove)

    def __mapActiveButtons__(self):
        buttons = []
        for name in self.wm.buttons.BUTTONS:
            active = self.wm.buttons[name]
            if (active):
                buttons.append(self.__mapButton__(name))
        if (len(buttons) > 0):
            return buttons
        return [Qt.NoButton]

    def __mapActiveMouseButtons__(self):
        buttons = self.__mapActiveButtons__()
        qtButtons = Qt.NoButton
        for b in buttons:
            if (b == Qt.RightButton or b == Qt.LeftButton or b == Qt.MidButton):
                qtButtons = qtButtons or b
        return qtButtons

    def __mapButton__(self, b):
        return WiiMotePointer.BUTTONMAP.get(b, Qt.NoButton)

    def __getLocalEventProperties__(self):

        widgetUnderPointer = self.qapp.widgetAt(self.point)  # type: QWidget
        if (not widgetUnderPointer):
            return (self.qapp, self.point)
        localPos = widgetUnderPointer.mapFromGlobal(self.point)

        return (widgetUnderPointer, localPos)

    def __sendEvent__(self, eventType, button=Qt.NoButton):

        qtButtons = self.__mapActiveMouseButtons__()

        targetWidget, localPos = self.__getLocalEventProperties__()

        localEvent = QMouseEvent(eventType, localPos, self.point, button, qtButtons, self.qapp.keyboardModifiers())
        localPointerEvent = PointerEvent(self, localEvent)
        self.qapp.postEvent(targetWidget, localPointerEvent)

    def __onButtonEvent__(self, ev):
        if (len(ev) > 0):
            for wmb in ev:
                pressed = wmb[1]
                eventType = QEvent.MouseButtonPress if pressed else QEvent.MouseButtonRelease
                mapped = self.__mapButton__(wmb[0])
                if mapped == Qt.RightButton:
                    # set or reset the current turn-operation
                    self.turnOperation = TurnOperation() if pressed else None

                self.__sendEvent__(eventType, mapped)
