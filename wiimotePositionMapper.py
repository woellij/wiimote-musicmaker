from matplotlib.pyplot import xlim, ylim

import numpy as np
from scipy.linalg import solve, inv

from operator import itemgetter

class WiiMotePositionMapper(object):
    markers = []
    DEST_W, DEST_H = 1366, 768
    # xlim(0, SRC_W)
    # ylim(0, SRC_H)
    # scatter(*zip(*scoords))  # repack points[] to axes[] for plottingd
    # scatter([SRC_W / 2], [SRC_H / 2], c='r', marker='+')

    def __init__(self):
        pass

    def map(self, data):

        if len(data) < 4 or len(data) > 4:
            return None


        irDots = list(map(lambda d: (d["x"], d["y"]), data))

        try:
            irDots = self.orderIrDots(irDots)
            irDots = self.filterMarkers(irDots)
            if len(irDots) < 4 or len(irDots) > 4:
                return None
            res = self.do(*irDots[0], *irDots[1], *irDots[2], *irDots[3], WiiMotePositionMapper.DEST_W, WiiMotePositionMapper.DEST_H )
            #res = self.do(irDots[0][0], irDots[0][1], irDots[1][0], irDots[1][1], irDots[2][0], irDots[2][1], irDofts[3][0], irDots[3][1], )
            return res
        except:
            pass
        return (0, 0)

    def orderIrDots(self, irDots):
        try:
            xSorted = list(sorted(irDots, key=itemgetter(0)))
            bottomLeft = min(irDots, key=itemgetter(1))
            xSorted.remove(bottomLeft)

            withDistance = list(map(lambda p: (p, np.linalg.norm(np.subtract(bottomLeft, p))), xSorted))

            distSorted = sorted(withDistance, key=itemgetter(1))
            return [distSorted[0][0], distSorted[2][0], distSorted[1][0], bottomLeft]
        except:
            return []

    def filterMarkers(self, irDots):
        return irDots


    def do(self, sx1, sy1, sx2, sy2, sx3, sy3, sx4, sy4, DEST_W, DEST_H):
        SRC_W, SRC_H = 1024, 768
        # Step 1
        source_points_123 = np.matrix([[sx1, sx2, sx3],
                                    [sy1, sy2, sy3],
                                    [1, 1, 1]])
        source_point_4 = [[sx4],
                          [sy4],
                          [1]]
        scale_to_source = solve(source_points_123, source_point_4)

        l, m, t = [float(x) for x in scale_to_source]
        unit_to_source = np.matrix([[l * sx1, m * sx2, t * sx3],
                                 [l * sy1, m * sy2, t * sy3],
                                 [l * 1, m * 1, t * 1]])


        dx1, dy1 = 0, 0
        dx2, dy2 = DEST_W, 0
        dx3, dy3 = DEST_W, DEST_H
        dx4, dy4 = 0, DEST_H
        dcoords = [(dx1, dy1), (dx2, dy2), (dx3, dy3), (dx4, dy4)]
        dest_points_123 = np.matrix([[dx1, dx2, dx3],
                                  [dy1, dy2, dy3],
                                  [1, 1, 1]])
        dest_point_4 = np.matrix([[dx4],
                               [dy4],
                               [1]])
        scale_to_dest = solve(dest_points_123, dest_point_4)
        l, m, t = [float(x) for x in scale_to_dest]

        unit_to_dest = np.matrix([[l * dx1, m * dx2, t * dx3],
                               [l * dy1, m * dy2, t * dy3],
                               [l * 1, m * 1, t * 1]])

        source_to_unit = inv(unit_to_source)
        source_to_dest = unit_to_dest @ source_to_unit

        x, y, z = [float(w) for w in (source_to_dest @ np.matrix([[SRC_W / 2],
                                                               [SRC_H / 2],
                                                               [1]]))]

        x = x / z
        y = y / z
        return(x, y)



