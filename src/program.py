    #!/usr/bin/python
# -*- coding: utf-8 -*-

from pyo import Server, sys

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import PyQt5.QtCore as qtcore

from wiimotePointer import *

from app import MusicMakerApp
from PyQt5 import QtWidgets, Qt
import atexit

s = None # type: Server
app = None # type: MusicMakerApp
filter = None

def onExit():
    if s:
        s.stop()
        s.shutdown()


class RemapMouseEventFilter(QObject):

    def __init__(self, qapp, widget):
        super(RemapMouseEventFilter, self).__init__()
        self.qapp= qapp  # type: Qt.QApplication
        self.widget = widget
        self.mousePointer = Pointer("mouse")

    def eventFilter(self, obj, event):
        if(type(event) is QMouseEvent):
            pointerEvent = PointerEvent(self.mousePointer, event)
            self.qapp.sendEvent(self.widget, pointerEvent)
            return True

        return False

def main():
    atexit.register(onExit)

    qapp = Qt.QApplication(sys.argv)

    app = MusicMakerApp(lambda ev: qapp.sendEvent(app, ev)) # type: QWidget
    app.showFullScreen()

    filter = RemapMouseEventFilter(qapp, app)
    qapp.installEventFilter(filter)

    """
    s = Server(sr=48000, nchnls=2, buffersize=512, duplex=0).boot()
    s.start()
    """

    """
    self.pointerReceiver = WiiMotePointerReceiver(lambda: WiiMotePointerConfig(WiiMotePositionMapper(),
                                                                               pointerEventCallback))
    self.pointerReceiver.start()
    """

    """
    s = QMouseEvent(QEvent.MouseButtonPress, QPoint(0,0), QPoint(0,0), qtcore.Qt.LeftButton, qtcore.Qt.LeftButton, qapp.keyboardModifiers())
    qapp.sendEvent(app, s)
    r = None
    for i in range(20):
        r = i * 10
        ev = QMouseEvent(QEvent.MouseMove, QPoint(r,r), qtcore.Qt.NoButton, qtcore.Qt.NoButton, qapp.keyboardModifiers())
        qapp.sendEvent(app, ev)

    s = QMouseEvent(QEvent.MouseButtonRelease, QPoint(r,r), qtcore.Qt.LeftButton, qtcore.Qt.LeftButton, qapp.keyboardModifiers())
    qapp.sendEvent(app, s)
    """

    sys.exit(qapp.exec_())





if __name__ == '__main__':
    main()