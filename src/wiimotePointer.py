import sys
import threading
import time

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCursor, QMouseEvent, QWindow, QWheelEvent
from PyQt5.QtWidgets import QUndoStack

import wiimote

class PointerEvent(QMouseEvent):
    def __init__(self, pointer, QMouseEvent):
        super(PointerEvent, self).__init__(QMouseEvent)
        self.pointer = pointer

class PointerWheelEvent(QWheelEvent):

    def __init__(self, pointer, pos):
        super(PointerWheelEvent, self).__init__(pos, pos)
        self.pointer = pointer

class Pointer(object):
    def __init__(self, id):
        super(Pointer, self).__init__()
        self.__id = id
        self.__undoStack = QUndoStack()

    def undoStack(self):
        return self.__undoStack

    def id(self): # type: str
        return self.__id

class WiiMotePointer(Pointer):

    def __init__(self, wiimote, config):
        super(WiiMotePointer, self).__init__(wiimote.btaddr)
        self.wm = wiimote  # type: wiimote.WiiMote
        self.config = config  # type: WiiMotePointerConfig
        self.wm.buttons.register_callback(self.__onButtonEvent__)
        self.wm.accelerometer.register_callback(self.__onAccelerometerData__)
        self.wm.ir.register_callback()

    def __onAccelerometerData__(self, data):
        if(self.buttons):
            for b in self.buttons:
                if b[0] is "A":
                    x, y = self.config.positionMapper.map(data)
                    ev = PointerWheelEvent(self, QPoint(x, y))
                    # TODO calculate angle
        pass

    def __onIrData__(self, data):
        x, y = self.config.positionMapper.map(data)
        # TODO create mouse event and map buttons

        ev = QMouseEvent()

        self.config.pointerEventCallback(ev)

    def __onButtonEvent__(self, ev):
        self.buttons = ev


class WiiMotePositionMapper(object):
    markers = []

    def __init__(self):
        pass

    def map(self, data):
        pass


class WiiMotePointerConfig(object):
    def __init__(self, positionMapper, pointerEventCallback):
        super(WiiMotePointerConfig, self).__init__()
        self.positionMapper = positionMapper
        self.pointerEventCallback = pointerEventCallback


class WiiMotePointerReceiver(object):
    def __init__(self, configFactory):
        super(WiiMotePointerReceiver, self).__init__()
        self.configFactory = configFactory  # type WiiMotePointerConfig
        self.connecteds = []
        self.thread = None


    def start(self):
        self.running = True
        if(self.thread):
            # already running
            return
        self.thread = threading.Thread(target=self.__run__, args=())
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread = None

    def __checkConnected__(self):
        for wm in self.connecteds[:]:
            wm = wm  # type: wiimote.WiiMote
            if (wm.connected):
                self.connecteds.remove(wm)

    def __discover__(self):
        try:
            pairs = wiimote.find()
            if (pairs):
                for p in pairs:
                    addr, name = p
                    try:
                        wm = wiimote.connect(addr, name)
                        if (wm not in self.connecteds):
                            pointer = WiiMotePointer(wm, self.configFactory())
                            self.connecteds.append(wm)
                    except:
                        pass
        except Exception as e:
            print(e.message)

    def __run__(self):
        while (self.running):
            time.sleep(1)
            self.__checkConnected__()
            self.__discover__()