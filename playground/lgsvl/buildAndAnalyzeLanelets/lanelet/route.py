import matplotlib.pyplot as plt
from .common import Common


class Route:
    def __init__(self, predecessor, intersection, successor, starting_point, ending_point, interpolated_points):
        self.predecessor = predecessor
        self.intersection = intersection
        self.successor = successor
        self.starting_point = starting_point
        self.ending_point = ending_point
        self.interpolated_points = interpolated_points
        self.feature_vector = None
        self.dc = None
        self.mr = None

    def visualize(self):
        # Oracle is the UNION of the AREAs OF THOSE LANELETS
        oracle_polygons = [self.predecessor.convert_to_polygon().shapely_object,
                           self.intersection.convert_to_polygon().shapely_object,
                           self.successor.convert_to_polygon().shapely_object]

        postiv_path = (self.predecessor, self.intersection, self.successor)
        print("PATH:", [l.lanelet_id for l in postiv_path])

        # Starting point
        start_point = self.starting_point
        end_point = self.ending_point

        fig = plt.figure()

        for i in range(0, len(start_point) - 1):
            plt.plot(*start_point[i], "o")
            plt.plot(*end_point[i], "x")

        Common.plot_polygon(oracle_polygons[0])
        Common.plot_polygon(oracle_polygons[1])
        Common.plot_polygon(oracle_polygons[2])
        plt.show()
