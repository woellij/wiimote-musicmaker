from matplotlib.pyplot import xlim, ylim
from numpy import *
from scipy.linalg import solve, inv


class WiiMotePositionMapper(object):
    markers = []

    # xlim(0, SRC_W)
    # ylim(0, SRC_H)
    # scatter(*zip(*scoords))  # repack points[] to axes[] for plottingd
    # scatter([SRC_W / 2], [SRC_H / 2], c='r', marker='+')

    def __init__(self):
        pass

    def map(self, data):
        if len(data) < 4 or len(data) > 4:
            return None

        ms = list(map(lambda d: (d["x"], d["y"]), data))


        ms = sort(ms,0,)
        print(ms)
        try:
            res = self.do(ms[0][0], ms[0][1], ms[1][0], ms[1][1], ms[2][0], ms[2][1], ms[3][0], ms[3][1], 1366, 768 )
            print(res)


            return res
        except:
            pass
        return (0, 0)

    def filterMarkers(self, data):
        markerDistance = ""


    def do(self, sx1, sy1, sx2, sy2, sx3, sy3, sx4, sy4, DEST_W, DEST_H):
        SRC_W, SRC_H = 1024, 768
        # Step 1
        source_points_123 = matrix([[sx1, sx2, sx3],
                                    [sy1, sy2, sy3],
                                    [1, 1, 1]])
        source_point_4 = [[sx4],
                          [sy4],
                          [1]]
        scale_to_source = solve(source_points_123, source_point_4)

        l, m, t = [float(x) for x in scale_to_source]
        unit_to_source = matrix([[l * sx1, m * sx2, t * sx3],
                                 [l * sy1, m * sy2, t * sy3],
                                 [l * 1, m * 1, t * 1]])


        dx1, dy1 = 0, 0
        dx2, dy2 = DEST_W, 0
        dx3, dy3 = DEST_W, DEST_H
        dx4, dy4 = 0, DEST_H
        dcoords = [(dx1, dy1), (dx2, dy2), (dx3, dy3), (dx4, dy4)]
        dest_points_123 = matrix([[dx1, dx2, dx3],
                                  [dy1, dy2, dy3],
                                  [1, 1, 1]])
        dest_point_4 = matrix([[dx4],
                               [dy4],
                               [1]])
        scale_to_dest = solve(dest_points_123, dest_point_4)
        l, m, t = [float(x) for x in scale_to_dest]

        unit_to_dest = matrix([[l * dx1, m * dx2, t * dx3],
                               [l * dy1, m * dy2, t * dy3],
                               [l * 1, m * 1, t * 1]])

        source_to_unit = inv(unit_to_source)
        source_to_dest = unit_to_dest @ source_to_unit

        x, y, z = [float(w) for w in (source_to_dest @ matrix([[SRC_W / 2],
                                                               [SRC_H / 2],
                                                               [1]]))]

        x = x / z
        y = y / z
        return(x, y)



