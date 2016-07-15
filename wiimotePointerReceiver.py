import threading
import time

import wiimote


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
        connected = list(self.connecteds.items())
        for entry in map(lambda pair: pair, connected):
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
