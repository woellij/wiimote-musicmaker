
from pyo import *
from knob import KnobListener


class SynthSound(KnobListener):

    def __init__(self):
        super(KnobListener, self).__init__()

        wav = SquareTable()
        env = CosTable([(0, 0), (100, 1), (500, .3), (8191, 0)])
        met = Metro(.125, 12).play()
        amp = TrigEnv(met, table=env, mul=.1)
        pit = TrigXnoiseMidi(met, dist='loopseg', x1=20, scale=1, mrange=(48, 84))
        out = Osc(table=wav, freq=pit, mul=amp).out()




    def onValueChange(self, value):
        print "listener change" + str(value)