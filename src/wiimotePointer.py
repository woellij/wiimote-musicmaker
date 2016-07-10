import sys
import threading
import time

import PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QUndoStack
from PyQt5.QtWidgets import QWidget

import wiimote

from pointer import *


class WiiMotePointer(Pointer):
    BUTTONMAP = {'A': Qt.RightButton,
                 'B': Qt.LeftButton,
                 'Down': Qt.Key_Down,
                 'Home': Qt.MiddleButton,
                 'Left': Qt.Key_Left,
                 'Minus': Qt.BackButton,
                 'One': Qt.Key_1,
                 'Plus': Qt.ForwardButton,
                 'Right': Qt.Key_Right,
                 'Two': Qt.Key_2,
                 'Up': Qt.Key_Up,
                 }

    def __init__(self, wiimote, qapp, color):
        super(WiiMotePointer, self).__init__(wiimote.btaddr, color)

        self.positionMapper = WiiMotePositionMapper()
        self.qapp = qapp  # type: QApplication
        self.point = QPoint(0, 0)

        self.wm = wiimote  # type: wiimote.WiiMote
        self.wm.buttons.register_callback(self.__onButtonEvent__)
        self.wm.accelerometer.register_callback(self.__onAccelerometerData__)
        self.wm.ir.register_callback(self.__onIrData__)

    def __onAccelerometerData__(self, data):
        for b in self.__mapActiveButtons__():
            if b == Qt.RightButton:
                print "sending wheel event"
                targetWidget, localPos = self.__getLocalEventProperties__()
                wheelEv = QWheelEvent(localPos, self.point, Qt.NoButton, self.__mapActiveButtons__(),
                                      self.qapp.keyboardModifiers())
                ev = PointerWheelEvent(self, wheelEv)
                self.qapp.sendEvent(targetWidget, ev)

    def __onIrData__(self, data):
        x, y = self.positionMapper.map(data)
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

    def __mapButton__(self, b):
        return WiiMotePointer.BUTTONMAP.get(b, Qt.NoButton)

    def __getLocalEventProperties__(self):

        widgetUnderPointer = self.qapp.widgetAt(self.point)  # type: QWidget
        if (not widgetUnderPointer):
            return (self.qapp, self.point)
        localPos = widgetUnderPointer.mapFromGlobal(self.point)

        return (widgetUnderPointer, localPos)

    def __sendEvent__(self, eventType, button=Qt.NoButton):

        buttons = self.__mapActiveButtons__()

        qtButtons = Qt.NoButton
        for b in buttons:
            if (b == Qt.RightButton or b == Qt.LeftButton or b == Qt.MidButton):
                qtButtons = qtButtons or b

        targetWidget, localPos = self.__getLocalEventProperties__()

        print "sending local pointer event to " + str(type(targetWidget))

        localEvent = QMouseEvent(eventType, localPos, self.point, button, qtButtons, self.qapp.keyboardModifiers())
        localPointerEvent = PointerEvent(self, localEvent)
        self.qapp.sendEvent(targetWidget, localPointerEvent)

    def __onButtonEvent__(self, ev):
        if (len(ev) > 0):
            for wmb in ev:
                eventType = QEvent.MouseButtonPress if wmb[1] else QEvent.MouseButtonRelease
                self.__sendEvent__(eventType, self.__mapButton__(wmb[0]))


class WiiMotePositionMapper(object):
    markers = []

    def __init__(self):
        pass

    def map(self, data):
        # TODO
        return (0, 0)


class WiiMotePointerReceiver(object):
    def __init__(self, pointerFactory):
        super(WiiMotePointerReceiver, self).__init__()
        self.pointerFactory = pointerFactory  # type WiiMotePointerConfig
        self.connecteds = dict()
        self.thread = None

    def start(self):
        self.running = True
        if (self.thread):
            # already running
            return
        self.thread = threading.Thread(target=self.__run__, args=())
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread = None

    def dispose(self):
        for wm in map(lambda pair: pair[1][0], self.connecteds.items()):
            wm.disconnect()

    def __checkConnected__(self):
        for entry in map(lambda pair: pair, self.connecteds.items()):
            wm = entry[1][0]  # type: wiimote.WiiMote
            if not wm.connected:
                try:
                    wiimote.connect(wm.btaddr, wm.model)
                except:
                    pass

    def __discover__(self):
        pairs = wiimote.find()
        if (pairs):
            for addr, name in pairs:
                if addr in self.connecteds:
                    continue
                wm = wiimote.connect(addr, name)
                pointer = self.pointerFactory(wm)
                self.connecteds[addr] = (wm, pointer)

    def __run__(self):
        while (self.running):
            time.sleep(1)
            self.__checkConnected__()
            self.__discover__()
