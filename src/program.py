# !/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget

from src.capturePointerDownWheelFilter import PointerDownCaptureWheelFilter
from src.dragEventFilter import DragEventFilter
from src.pointerEventFilter import *
from src.wiimotePointer import *
from src.remapMouseEventFilter import *

from src.app import MusicMakerApp
from PyQt5 import Qt
import atexit

program = None  # type: Program


def onExit():
    if (program):
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

        self.undoRedoFilter = PointerUndoRedoEventFilter()
        qapp.installEventFilter(self.undoRedoFilter)

        self.wheelFilter = PointerDownCaptureWheelFilter(qapp)
        qapp.installEventFilter(self.wheelFilter)

        self.sendPointerEventToFirstPlayWidgetFilter = SendPointerEventToFirstPlayWidgetFilter(qapp)
        qapp.installEventFilter(self.sendPointerEventToFirstPlayWidgetFilter)

        """self.s = Server(sr=48000, nchnls=2, buffersize=512, duplex=0).boot()
        self.s.start()"""

        # TODO generate random colors
        pointerFactory = lambda wm: WiiMotePointer(wm, qapp, Qt.Qt.yellow)
        pointerReceiver = WiiMotePointerReceiver(pointerFactory)
        pointerReceiver.start()

    def onExit(self):
        if hasattr(self, "s"):
            self.s.stop()
            self.s.shutdown()
        if hasattr(self, "pointerReceiver"):
            self.pointerReceiver.dispose()


def main():
    atexit.register(onExit)
    program = Program()

    screen_resolution = program.qapp.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    widthDif, heightDif = 50, 50
    width, height = width - widthDif, height - heightDif
    WiiMotePositionMapper.markers.append((widthDif, heightDif))
    WiiMotePositionMapper.markers.append((width, - heightDif))
    WiiMotePositionMapper.markers.append((widthDif, height))
    WiiMotePositionMapper.markers.append((width, height))

    sys.exit(program.qapp.exec_())


if __name__ == '__main__':
    main()
