import sys
import threading
import time

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCursor, QMouseEvent, QWindow, QWheelEvent
from PyQt5.QtWidgets import QUndoStack

import wiimote

from pointer import *

class WiiMotePointer(Pointer):

    def __init__(self, wiimote, config):
        super(WiiMotePointer, self).__init__(wiimote.btaddr, config.color)
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
    def __init__(self, positionMapper, pointerEventCallback, color):
        super(WiiMotePointerConfig, self).__init__()
        self.positionMapper = positionMapper
        self.color = color
        self.pointerEventCallback = pointerEventCallback


class WiiMotePointerReceiver(object):
    def __init__(self, configFactory):
        super(WiiMotePointerReceiver, self).__init__()
        self.configFactory = configFactory  # type WiiMotePointerConfig
        self.connecteds = dict()
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
                    pointer = WiiMotePointer(wm, self.configFactory())
                    self.connecteds[addr] = (wm, pointer)

    def __run__(self):
        while (self.running):
            time.sleep(1)
            self.__checkConnected__()
            self.__discover__()