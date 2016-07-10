    #!/usr/bin/python
# -*- coding: utf-8 -*-

from pyo import Server, sys

from PyQt5.QtWidgets import QWidget
from pointerEventFilter import PointerEventFilter
from wiimotePointer import *
from remapMouseEventFilter import *

from app import MusicMakerApp
from PyQt5 import Qt
import atexit

s = None # type: Server
app = None # type: MusicMakerApp
pointerFilter = None
filter = None
pointerReceiver = None

def onExit():
    if s:
        s.stop()
        s.shutdown()
    if pointerReceiver:
        pointerReceiver.dispose()



def main():
    atexit.register(onExit)

    qapp = Qt.QApplication(sys.argv)

    app = MusicMakerApp() # type: QWidget
    app.show()

    filter = RemapMouseEventFilter(qapp, app)
    qapp.installEventFilter(filter)

    pointerFilter = PointerEventFilter(app, qapp)
    qapp.installEventFilter(pointerFilter)

    """
    s = Server(sr=48000, nchnls=2, buffersize=512, duplex=0).boot()
    s.start()
    """
    wiiMotePointerCallback = lambda ev: qapp.sendEvent(app, ev)
    configFactory = lambda:  WiiMotePointerConfig(WiiMotePositionMapper(), configFactory,  wiiMotePointerCallback)
    pointerReceiver = WiiMotePointerReceiver(configFactory)
    pointerReceiver.start()
    """


                widgetUnderPointer = self.qapp.widgetAt(ev.pos())  # type: QWidget

                if (widgetUnderPointer):
                    localPos = widgetUnderPointer.mapFromGlobal(ev.globalPos())

                    print "sending local pointer event to " + str(type(widgetUnderPointer))
                    localEvent = QMouseEvent(ev.type(), localPos, ev.globalPos(), ev.button(), ev.buttons(), ev.modifiers())
                    localPointerEvent = PointerEvent(ev.pointer, localEvent)
                    self.qapp.sendEvent(widgetUnderPointer, localPointerEvent)
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