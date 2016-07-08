import sys
import threading
import time

from PyQt5.QtGui import QCursor, QMouseEvent, QWindow
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
        # TODO create mouse event and map buttons

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

    def __checConnected__(self):
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
            self.__checConnected__()
            self.__discover__()