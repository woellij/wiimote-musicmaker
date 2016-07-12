from numpy import *
from scipy.linalg import solve


class WiiMotePositionMapper(object):
    markers = []

    # xlim(0, SRC_W)
    # ylim(0, SRC_H)
    # scatter(*zip(*scoords))  # repack points[] to axes[] for plottingd
    # scatter([SRC_W / 2], [SRC_H / 2], c='r', marker='+')

    def __init__(self):
        pass

    def map(self, data):
        # TODO
        return (0, 0)

    def do(self, sx1, sx2, sx3, sy1, sy2, sy3, sx4, sy4):
        # Step 1
        source_points_123 = matrix([[sx1, sx2, sx3],
                                    [sy1, sy2, sy3],
                                    [1, 1, 1]])
        source_point_4 = [[sx4],
                          [sy4],
                          [1]]
        scale_to_source = solve(source_points_123, source_point_4)
