    #!/usr/bin/python
# -*- coding: utf-8 -*-

from pyo import Server, sys

from PyQt5.QtWidgets import QWidget
from pointerEventFilter import PointerEventFilter, DragEventFilter
from wiimotePointer import *
from remapMouseEventFilter import *

from app import MusicMakerApp
from PyQt5 import Qt
import atexit

program = None

def onExit():
    if(program):
        program.onExit()

class Program(object):
    def __init__(self):
        super(Program, self).__init__()

        self.qapp = qapp = Qt.QApplication(sys.argv)
        app = MusicMakerApp()  # type: QWidget
        app.show()

        self.remapMousefilter = RemapMouseEventFilter(qapp)
        qapp.installEventFilter(self.remapMousefilter)

        self.pointerFilter = PointerEventFilter(app, qapp)
        qapp.installEventFilter(self.pointerFilter)

        self.dragFilter = DragEventFilter(qapp)
        qapp.installEventFilter(self.dragFilter)

        """
           s = Server(sr=48000, nchnls=2, buffersize=512, duplex=0).boot()
           s.start()
           """
        # TODO generate random colors
        pointerFactory = lambda wm: WiiMotePointer(wm, qapp, Qt.Qt.yellow)
        pointerReceiver = WiiMotePointerReceiver(pointerFactory)
        pointerReceiver.start()

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

    def onExit(self):
        if hasattr(self, "s"):
            self.s.stop()
            self.s.shutdown()
        if hasattr(self, "pointerReceiver"):
            self.pointerReceiver.dispose()

def main():
    atexit.register(onExit)
    program = Program()

    sys.exit(program.qapp.exec_())

if __name__ == '__main__':
    main()