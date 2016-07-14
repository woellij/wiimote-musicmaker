# !/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget

from src.capturePointerDownWheelFilter import PointerDownCaptureWheelFilter
from src.dragEventFilter import DragEventFilter
from src.drawWidget import PointerDrawEventFilter
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


class ColorPick(object):
    from PyQt5.QtCore import Qt as qt
    COLORS = [qt.white, qt.green, qt.yellow, qt.cyan, qt.red, qt.darkYellow, qt.darkCyan, qt.darkGreen]

    def __init__(self):
        super(ColorPick, self).__init__()
        self.index = 0

    def pick(self):
        self.index += 1
        self.index = (self.index % len(ColorPick.COLORS)) - 1
        print(self.index)
        return ColorPick.COLORS[self.index]


class Program(object):
    def __init__(self):
        super(Program, self).__init__()

        self.qapp = qapp = Qt.QApplication(sys.argv)

        self.sendPointerEventToFirstPlayWidgetFilter = SendPointerEventToFirstPlayWidgetFilter(qapp)
        qapp.installEventFilter(self.sendPointerEventToFirstPlayWidgetFilter)

        app = MusicMakerApp()  # type: QWidget
        app.showFullScreen()

        self.pointerDrawFilter = PointerDrawEventFilter(app, None)
        self.qapp.installEventFilter(self.pointerDrawFilter)

        app.setPointerDrawFilter(self.pointerDrawFilter)


        self.colorPick = ColorPick()
        self.remapMousefilter = RemapMouseEventFilter(qapp, self.colorPick)
        qapp.installEventFilter(self.remapMousefilter)




        self.pointerFilter = PointerEventFilter(app, qapp)
        qapp.installEventFilter(self.pointerFilter)

        self.dragFilter = DragEventFilter(qapp)
        qapp.installEventFilter(self.dragFilter)

        self.undoRedoFilter = PointerUndoRedoEventFilter()
        qapp.installEventFilter(self.undoRedoFilter)

        self.wheelFilter = PointerDownCaptureWheelFilter(qapp)
        qapp.installEventFilter(self.wheelFilter)


        """self.s = Server(sr=48000, nchnls=2, buffersize=512, duplex=0).boot()
        self.s.start()"""

        pointerFactory = lambda wm: WiiMotePointer(wm, qapp, self.colorPick.pick())
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
    widthDif, heightDif = 0, 0
    width, height = width - widthDif, height - heightDif
    WiiMotePositionMapper.markers.append((widthDif, heightDif))
    WiiMotePositionMapper.markers.append((width, - heightDif))
    WiiMotePositionMapper.markers.append((widthDif, height))
    WiiMotePositionMapper.markers.append((width, height))

    WiiMotePositionMapper.DEST_W = screen_resolution.width() + 2 * widthDif
    WiiMotePositionMapper.DEST_H = screen_resolution.height() + 2 * heightDif

    sys.exit(program.qapp.exec_())


if __name__ == '__main__':
    main()
