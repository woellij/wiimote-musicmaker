import sys
import threading
from PyQt5 import uic, QtWidgets

import time

from PyQt5.QtGui import QCursor, QMouseEvent

from knob import Knob
from Sounds import SynthSound
import wiimote


class WiiMotePointer(object):
    def __init__(self, wiimote, config):
        self.wm = wiimote  # type: wiimote.WiiMote
        self.config = config  # type: WiiMotePointerConfig
        self.wm.buttons.register_callback(self.__onButtonEvent__)
        self.wm.ir.register_callback()
        self.id = self.wm.btaddr

    def __onIrData__(self, data):
        x, y = self.config.positionMapper.map(data)
        # TODO create mouse event
        ev = QMouseEvent()
        self.config.pointerEventCallback(ev)

    def __onButtonEvent__(self, ev):
        self.buttons = ev


class WiiMotePositionMapper(object):
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
    def __init__(self, callback, configFactory):
        super(WiiMotePointerReceiver, self).__init__()
        self.callback = callback
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

    def __checConnected__(self):
        for wm in [self.connecteds]:
            wm = wm  # type: wiimote.WiiMote
            if (wm.connected):
                self.connecteds.remove(wm)

    def __discover__(self):
        pairs = wiimote.find()
        if (pairs):
            for p in pairs:
                addr, name = p
                try:
                    wm = wiimote.connect(addr, name)
                    if (wm not in self.connecteds):
                        pointer = WiiMotePointer(wm, self.configFactory())
                        self.callback(pointer)
                        self.connecteds.append(wm)
                except:
                    pass

    def __run__(self):
        while (self.running):
            time.sleep(1)
            self.__checConnected__()
            self.__discover__()


class MusicMakerApp(QtWidgets.QWindow):
    def __init__(self,  pointerEventCallback):
        super(MusicMakerApp, self).__init__()

        self.k = k = Knob(SynthSound(), 0, 100)
        k.setParent(self)

        self.pointerReceiver = WiiMotePointerReceiver(self.onPointerReceived,
                                                      lambda: WiiMotePointerConfig(WiiMotePositionMapper(),
                                                                                   pointerEventCallback))
        self.pointerReceiver.start()