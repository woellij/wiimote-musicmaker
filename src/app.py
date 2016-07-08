from PyQt5 import uic, QtWidgets

from knob import Knob
from Sounds import SynthSound
from drawWidget import QDrawWidget
from wiimotePointer import *


class MusicMakerApp(QDrawWidget):
    def __init__(self, pointerEventCallback):
        super(MusicMakerApp, self).__init__(self.onComplete)

        self.k = k = Knob(SynthSound(), 0, 100)
        k.setParent(self)

        self.pointerReceiver = WiiMotePointerReceiver(lambda: WiiMotePointerConfig(WiiMotePositionMapper(),
                                                                                   pointerEventCallback))
        self.pointerReceiver.start()

    def onComplete(self, points):
        print points
