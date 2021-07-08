from typing import List, Tuple
import numpy as np
from shapely.geometry import LineString
from shapely.affinity import translate, rotate
from math import atan2, pi

AngleLength = Tuple[float, float]
ListOfAngleLength = List[AngleLength]

Point = Tuple[float, float]
ListOfPoints = List[Point]


def _standardize(list_of_points):
    middle_line_x = [p[0] for p in list_of_points]
    middle_line_y = [p[1] for p in list_of_points]
    middle_line = LineString(zip(middle_line_x, middle_line_y))

    translate_to_origin_x = - list_of_points[0][0]
    translate_to_origin_y = - list_of_points[0][1]

    middle_line = translate(middle_line, xoff=translate_to_origin_x, yoff=translate_to_origin_y, zoff=0.0)

    # Rotate
    # https://www.quora.com/What-is-the-angle-between-the-vector-A-2i+3j-and-y-axis#:~:text=If%20we%20wish%20to%20find,manipulate%20the%20dot%20product%20equation.

    delta_y = middle_line_y[1] - middle_line_y[0]
    delta_x = middle_line_x[1] - middle_line_x[0]

    current_angle = atan2(delta_y, delta_x)

    middle_line = rotate(middle_line, (pi / 2) - current_angle, origin=(0, 0), use_radians=True)

    # list(zip(*p.exterior.coords.xy))

    return list(zip(*middle_line.coords.xy))


def _calc_cost_discrete(u: AngleLength, v: AngleLength):
    delta_angle, delta_len = np.subtract(u, v)
    #print(delta_angle)
    delta_angle = np.abs((delta_angle + 180) % 360 - 180)
    #print(str(delta_angle))
    eps_angle = 0.3
    eps_len = 0.2
    if delta_angle < eps_angle and delta_len < eps_len:
        res = 0
    else:
        res = 2

    #res = 1 / 2 * (delta_angle / (1 + delta_angle) + delta_len / (1 + delta_len))
    return res

def _calc_cost_weighted(u: AngleLength, v: AngleLength):
    delta_angle, delta_len = np.abs(np.subtract(u, v))
    delta_angle = np.abs((delta_angle + 180) % 360 - 180)
    eps_angle = 0.3
    eps_len = 0.2
    if delta_angle < eps_angle and delta_len < eps_len:
        res = 0
    else:
        res = 1 / 2 * (delta_angle / (1 + delta_angle) + delta_len / (1 + delta_len))
    return res



#_calc_cost = _calc_cost_discrete
_calc_cost = _calc_cost_weighted


def _iterative_levenshtein_dist_angle(s: ListOfAngleLength, t: ListOfAngleLength):
    """
        iterative_levenshtein(s, t) -> ldist
        ldist is the Levenshtein distance between the strings
        s and t.
        For all i and j, dist[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    rows = len(s) + 1
    cols = len(t) + 1
    dist = [[0 for x in range(cols)] for x in range(rows)]
    # source prefixes can be transformed into empty strings
    # by deletions:
    for i in range(1, rows):
        dist[i][0] = i
    # target prefixes can be created from an empty source string
    # by inserting the characters
    for i in range(1, cols):
        dist[0][i] = i


    for col in range(1, cols):
        for row in range(1, rows):
            cost = _calc_cost(s[row - 1], t[col - 1])
            dist[row][col] = min(dist[row - 1][col] + 1,  # deletion
                                 dist[row][col - 1] + 1,  # insertion
                                 dist[row - 1][col - 1] + cost)  # substitution
    # for r in range(rows):
    #     print(dist[r])

    return dist[row][col]


def _calc_angle_distance(v0, v1):
    at_0 = np.arctan2(v0[1], v0[0])
    at_1 = np.arctan2(v1[1], v1[0])
    return at_1 - at_0


# TODO This
def _calc_dist_angle(points: ListOfPoints) -> ListOfAngleLength:
    assert len(points) >= 2, f'at least two points are needed'

    def vector(idx):
        return np.subtract(points[idx + 1], points[idx])

    n = len(points) - 1
    result: ListOfAngleLength = [None] * (n)
    b = vector(0)
    for i in range(n):
        a = b
        b = vector(i)
        angle = _calc_angle_distance(a, b)
        distance = np.linalg.norm(b)
        result[i] = (angle, distance, [points[i+1], points[i]])
    return result

def iterative_levenshtein(s_raw: ListOfPoints, t_raw: ListOfPoints):

    s_std = _standardize(s_raw)
    t_std = _standardize(t_raw)

    s_da = _calc_dist_angle(s_std)
    t_da = _calc_dist_angle(t_std)

    # Extract ONLY angle and length
    s = [(v[0], v[1]) for v in s_da]
    t = [(v[0], v[1]) for v in t_da]

    return _iterative_levenshtein_dist_angle(s, t)

if __name__ == '__main__':
    import unittest


    class TestDist(unittest.TestCase):

        def setUp(self):
            self.s = [(0, 0), (0, 2), (2, 2)]
            self.t = [(0, 0), (0, 2), (-2, 2)]

        def test_dist_angle_calculations(self):
            self.assertEqual(_calc_dist_angle(self.s), [(0, 2), (-90, 2)])
            self.assertEqual(_calc_dist_angle(self.t), [(0, 2), (90, 2)])

        def test_iterative_levenshtein_dist_angle(self):
            s = [(2, -90), (2, 0)]
            t = [(2, -90), (2, 0)]
            dist = _iterative_levenshtein_dist_angle(s, t)
            self.assertEqual(dist, 0)

        def test_iterative_levenshtein(self):
            dist = iterative_levenshtein(self.t, self.s)
            self.assertNotEqual(dist, 0)


    unittest.main()
