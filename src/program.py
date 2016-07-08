#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyo import Server, sys

from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QWidget

from app import MusicMakerApp
from PyQt5 import QtWidgets, Qt
import atexit

s = None # type: Server
app = None # type: MusicMakerApp

def onExit():
    if s:
        s.stop()
        s.shutdown()

def main():
    atexit.register(onExit)
    s = Server(sr=48000, nchnls=2, buffersize=512, duplex=0).boot()
    s.start()

    qapp = Qt.QApplication(sys.argv)

    app = MusicMakerApp(lambda ev: qapp.sendEvent(app, ev)) # type: QWidget
    app.showFullScreen()

    sys.exit(qapp.exec_())



if __name__ == '__main__':
    main()