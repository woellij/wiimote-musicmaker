import time

import numpy as np

from oneEuroFilter import OneEuroFilter


"""
Based on Sourcecode found on http://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
'Angles between two n-dimensional vectors in Python'
"""

def unit_vector(vector):
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    try:
        v1_u = unit_vector(v1)
        v2_u = unit_vector(v2)
        directed = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])

        angle = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
        angle = angle * 360 / 2 / np.pi
        return angle, directed
    except:
        return 0


class TurnOperation(object):
    def __init__(self):
        config = {
            'freq': 120,  # Hz
            'mincutoff': 1,  #
            'beta': 0.1,  #
            'dcutoff': 1.0  # this one should be ok
        }

        self.angleFilter = OneEuroFilter(**config)
        self.latestNormal = (0, 0)

    def getAngle(self, data):
        dif = 512.5
        x, y = data[0] - dif, data[2] - dif
        currentNormal = np.array([x, 0]) + np.array([0, y])
        angle, directed = angle_between(currentNormal, self.latestNormal)

        self.latestNormal = (0, 0)

        self.latestNormal = currentNormal

        if not np.isnan(angle):
            factor = 1 if directed > 0 else -1
            angle = angle * factor
            angle = self.angleFilter(angle, time.time())
            return angle
        return None
