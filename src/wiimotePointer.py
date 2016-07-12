import sys
import threading
import time

import PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QUndoStack
from PyQt5.QtWidgets import QWidget

from src import wiimote
from src.oneEuroFilter import *
import time
import src.wiimote

from src.pointer import *
import numpy as np

from src.wiimotePositionMapper import WiiMotePositionMapper


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    try:
        v1_u = unit_vector(v1)
        v2_u = unit_vector(v2)
        directed = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)), directed
    except:
        return 0


class WiiMotePointer(Pointer):
    BUTTONMAP = {'A': Qt.RightButton,
                 'B': Qt.LeftButton,
                 'Down': Qt.Key_Down,
                 'Home': Qt.MiddleButton,
                 'Left': Qt.Key_Left,
                 'Minus': Qt.BackButton,
                 'One': Qt.ExtraButton3,
                 'Plus': Qt.ForwardButton,
                 'Right': Qt.Key_Right,
                 'Two': Qt.ExtraButton4,
                 'Up': Qt.Key_Up,
                 }

    def __init__(self, wiimote, qapp, color):
        super(WiiMotePointer, self).__init__(wiimote.btaddr, color)

        self.positionMapper = WiiMotePositionMapper()
        self.qapp = qapp  # type: QApplication
        self.point = QPoint(0, 0)
        self.latestNormal = (0, 0)

        self.wm = wiimote  # type: wiimote.WiiMote
        self.wm.buttons.register_callback(self.__onButtonEvent__)
        self.wm.accelerometer.register_callback(self.__onAccelerometerData__)
        self.wm.ir.register_callback(self.__onIrData__)

        config = {
            'freq': 120,  # Hz
            'mincutoff': 0.1,  # FIXME
            'beta': 0.1,  # FIXME
            'dcutoff': 1.0  # this one should be ok
        }

        self.angleFilter = OneEuroFilter(**config)
        self.angles = []

    def __onAccelerometerData__(self, data):
        dif = 512
        x, y = data[0] - dif, data[2] - dif
        currentNormal = np.array([x, 0]) + np.array([0, y])

        angle, direction = angle_between(currentNormal, self.latestNormal)
        angle = angle * (180 / np.pi)
        angle = angle * -1 if direction < 0 else angle

        if not np.isnan(angle):
            angle = self.angleFilter(angle, time.time())

        for b in self.__mapActiveButtons__():
            if b == Qt.RightButton:
                # only sending wiimote wheelevent when right mouse button is pressed (mapped from A)
                # append values
                self.angles.append(angle)

                if len(self.angles) > 5:
                    angle = np.sum(self.angles)
                    self.angles = []

                    targetWidget, localPos = self.__getLocalEventProperties__()
                    wheelEv = QWheelEvent(localPos, self.point, QPoint(0, 0), QPoint(0, angle), abs(angle), Qt.Vertical,
                                          self.__mapActiveMouseButtons__(), self.qapp.keyboardModifiers())
                    ev = PointerWheelEvent(self, angle, wheelEv)
                    self.qapp.sendEvent(targetWidget, ev)

        self.latestNormal = currentNormal

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
        self.qapp.sendEvent(targetWidget, localPointerEvent)

    def __onButtonEvent__(self, ev):
        if (len(ev) > 0):
            for wmb in ev:
                eventType = QEvent.MouseButtonPress if wmb[1] else QEvent.MouseButtonRelease
                mapped = self.__mapButton__(wmb[0])
                if mapped == Qt.RightButton:
                    self.angles = []
                self.__sendEvent__(eventType, mapped)


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
                # remove to cleanup
                self.connecteds.pop(wm.btaddr, None)
                # try reconnect
                self.__connect__(wm.btaddr, wm.model)

    def __connect__(self, addr, name):
        try:
            wm = wiimote.connect(addr, name)
            pointer = self.pointerFactory(wm)
            self.connecteds[addr] = (wm, pointer)
            print("connected to: " + addr)
        except Exception as e:
            print("error connecting to : " + addr + " " + str(e))
            pass

    def __discover__(self):
        try:
            pairs = wiimote.find()
            if (pairs):
                for addr, name in pairs:
                    if addr in self.connecteds:
                        # already connected
                        continue
                    self.__connect__(addr, name)

        except:
            pass

    def __run__(self):
        while (self.running):
            time.sleep(1)
            self.__checkConnected__()
            self.__discover__()
