

import sys
from PyQt5 import uic, QtWidgets

from knob import Knob
from Sounds import SynthSound


class MusicMakerApp(QtWidgets.QDialog):
    def __init__(self,uiFile):
        super(MusicMakerApp, self).__init__()
        uic.loadUi(uiFile, self)

        k = Knob(SynthSound(), 0, 100)
        k.setParent(self)



