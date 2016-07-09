    #!/usr/bin/python
# -*- coding: utf-8 -*-

from pyo import Server, sys

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import PyQt5.QtCore as qtcore

from PointerWidget import PointerWidget
from wiimotePointer import *

from app import MusicMakerApp
from PyQt5 import QtWidgets, Qt
import PyQt5
import atexit

s = None # type: Server
app = None # type: MusicMakerApp
pointerFilter = None
filter = None

def onExit():
    if s:
        s.stop()
        s.shutdown()



class PointerEventFilter(QObject):
    def __init__(self, widget):
        super(PointerEventFilter, self).__init__()

        self.widget = widget # type: QWidget
        self.__pointers = dict()

    def pointers(self):
        return self.__pointers.values()

    def eventFilter(self, obj, event):
        if not type(event) is PointerEvent:
            return False
        ev = event # type: PointerEvent
        t = ev.type()
        if t == QMouseEvent.MouseMove:
            id = ev.pointer.id()
            pointerWidget = self.__pointers.get(id, None)
            if not pointerWidget:
                print "creating pointerwidget"
                pointerWidget = PointerWidget(obj, ev.pointer)
                self.__pointers[ev.pointer.id()] = pointerWidget
                pointerWidget.show()

            pointerWidget.move(ev.pos())

        return False


class RemapMouseEventFilter(QObject):

    def __init__(self, qapp, widget):
        super(RemapMouseEventFilter, self).__init__()
        self.qapp= qapp  # type: Qt.QApplication
        self.widget = widget # type: QWidget
        self.mousePointer = Pointer("mouse", PyQt5.QtCore.Qt.darkYellow)

    def eventFilter(self, obj, event):
        if(type(event) is QMouseEvent):
            wUnder = self.qapp.widgetAt(event.pos()) # type: QWidget
            if(wUnder):
                localPos = wUnder.mapFromGlobal(event.globalPos())
                e = event # type: QMouseEvent

                localevent = QMouseEvent(event.type(), localPos, e.globalPos(), e.button(), e.buttons(), e.modifiers())
                localPointerEvent = PointerEvent(self.mousePointer, localevent)
                self.qapp.sendEvent(wUnder, localPointerEvent)

            pointerEvent = PointerEvent(self.mousePointer, event)
            self.qapp.sendEvent(self.qapp, pointerEvent)
            return True

        return False

def main():
    atexit.register(onExit)

    qapp = Qt.QApplication(sys.argv)

    app = MusicMakerApp(lambda ev: qapp.sendEvent(app, ev)) # type: QWidget
    app.showFullScreen()

    filter = RemapMouseEventFilter(qapp, app)
    qapp.installEventFilter(filter)

    pointerFilter = PointerEventFilter(app)
    qapp.installEventFilter(pointerFilter)

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