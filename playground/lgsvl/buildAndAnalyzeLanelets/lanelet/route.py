import matplotlib.pyplot as plt
from .common import Common
import os
import json


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

    def to_json(self, directory, ID):
        # Create the directory
        path = "{}/data/{}".format(os.path.dirname(os.path.realpath(__file__)), directory)
        if os.path.exists(path) is False:
            os.mkdir(path)
            print("Directory '% s' created" % directory)
        fig = plt.figure()
        self.visualize()
        fig.savefig(
            "{}/data/{}/{}".format(os.path.dirname(os.path.realpath(__file__)), directory, str(ID) + "0.png"))

        # Starting point
        start_point = self.starting_point
        end_point = self.ending_point
        for i in range(0, len(start_point) - 1):
            fn = os.path.dirname(os.path.realpath(__file__)) + "/data/" + directory + '/' + str(ID) + str(i+1) + ".json"
            with open(fn, 'w') as fp:
                json.dump(
                    {
                        "start": [start_point[i][0], start_point[i][1]],
                        "end": [end_point[i][0], end_point[i][1]]
                    }
                    , fp)

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

        for i in range(0, len(start_point) - 1):
            plt.plot(*start_point[i], "o")
            plt.plot(*end_point[i], "x")

        Common.plot_polygon(oracle_polygons[0])
        Common.plot_polygon(oracle_polygons[1])
        Common.plot_polygon(oracle_polygons[2])
        plt.show()
