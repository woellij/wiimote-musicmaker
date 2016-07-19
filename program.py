# !/usr/bin/python
# -*- coding: utf-8 -*-

import atexit
import sys

from PyQt5 import Qt

from app import MusicMakerApp
from capturePointerDownWheelFilter import CapturePointerWheelEventFilter
from dragEventFilter import DragEventFilter
from drawWidget import PointerDrawEventFilter
from forwardPointerWheelEventFilter import SendPointerEventToFirstPlayWidgetFilter
from pointerEventFilter import PointerEventFilter
from remapMouseEventFilter import RemapMouseEventFilter
from undoPointerEventFilter import PointerUndoRedoEventFilter
from wiimotePointer import WiiMotePointer
from wiimotePointerReceiver import WiiMotePointerReceiver
from wiimotePositionMapper import WiiMotePositionMapper

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
        index = (self.index % len(ColorPick.COLORS)) - 1
        print(index)
        return ColorPick.COLORS[index]


class Program(object):
    def __init__(self):
        super(Program, self).__init__()

        self.qapp = qapp = Qt.QApplication(sys.argv)
        app = MusicMakerApp()  # type: QWidget
        app.show()
        app.setMouseTracking(True)

        self.colorPick = ColorPick()
        self.remapMousefilter = RemapMouseEventFilter(qapp, self.colorPick)
        qapp.installEventFilter(self.remapMousefilter)

        self.forwardPointerWheelEventToFirstWidget = SendPointerEventToFirstPlayWidgetFilter(qapp)
        qapp.installEventFilter(self.forwardPointerWheelEventToFirstWidget)



        self.pointerDrawFilter = PointerDrawEventFilter(app, None)
        qapp.installEventFilter(self.pointerDrawFilter)
        app.setPointerDrawFilter(self.pointerDrawFilter)

        self.dragFilter = DragEventFilter(qapp)
        qapp.installEventFilter(self.dragFilter)

        self.pointerFilter = PointerEventFilter(app, qapp)
        qapp.installEventFilter(self.pointerFilter)

        self.undoRedoFilter = PointerUndoRedoEventFilter()
        qapp.installEventFilter(self.undoRedoFilter)

        self.wheelFilter = CapturePointerWheelEventFilter(qapp)
        qapp.installEventFilter(self.wheelFilter)

        """self.s = Server(sr=48000, nchnls=2, buffersize=512, duplex=0).boot()
        self.s.start()"""

        pointerFactory = lambda wm: WiiMotePointer(wm, qapp, self.colorPick.pick())
        pointerReceiver = WiiMotePointerReceiver(pointerFactory)
        pointerReceiver.start()

        if (len(sys.argv) == 2):
            mac = sys.argv[1]
            # pointerReceiver.__connect__(mac, "Nintendo RVL-CNT-01-TR")

    def onExit(self):
        if hasattr(self, "pointerReceiver") and self.pointerReceiver:
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
