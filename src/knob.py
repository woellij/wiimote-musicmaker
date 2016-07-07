from PyQt5 import QtWidgets

class KnobListener(object):
    def __init__(self):
        pass

    def onValueChange(self, value):
        print value


class Knob(QtWidgets.QDial):
    def __init__(self, knobListener, min, max):
        super(Knob, self).__init__()
        self.setMaximum(max)
        self.setMinimum(min)

        self.listener = knobListener # type: KnobListener
        self.valueChanged.connect(self.listener.onValueChange)




