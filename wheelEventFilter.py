from PyQt5.QtCore import QObject
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QApplication

from playWidget import PlayWidget
from pointer import PointerWheelEvent


class WheelEventFilter(QObject):
    def __init__(self):
        super(WheelEventFilter, self).__init__()

    def adjustVolume(self, target, ev):
        vol = target.getVolume()

        if type(ev) is PointerWheelEvent:
            ev = ev  # type:PointerWheelEvent
            dif = ev.pointerAngleDelta * 2
            dif = dif / 180
            dif = vol * dif
            print("volume dif ", dif)
            vol += dif
        elif type(ev) is QWheelEvent:
            ev = ev  # type:QWheelEvent
            x, y = ev.angleDelta().x(), ev.angleDelta().y()

            changeVol = 0.05
            vol = vol + changeVol if y > 0 else vol - changeVol

        target.setVolume(vol)

    def eventFilter(self, obj, event):
        return False
        if type(event) is PointerWheelEvent or type(event) is QWheelEvent:
            ev = event # type: QWheelEvent
            target = QApplication.instance().widgetAt(event.globalPos()) # type: PlayWidget

            if type(target) != PlayWidget:
                print ("target not playwidget")
                return False
            self.adjustVolume(target, ev)
            return True
        return False



