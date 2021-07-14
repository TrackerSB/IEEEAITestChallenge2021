import matplotlib.pyplot as plt
from .common import Common
import os
import json
from ..correlation.utils import direction_coverage, min_radius


class Route:
    def __init__(self, predecessor, intersection, successor,
                 starting_point, ending_point, interpolated_points,
                 parking_point=None):
        self.predecessor = predecessor
        self.intersection = intersection
        self.successor = successor
        self.starting_point = starting_point
        self.ending_point = ending_point
        self.interpolated_points = interpolated_points
        self.parking_point = parking_point
        self.feature_vector, self.dc, self.mr = self._compute_feature_vector().values()

    def to_json(self, directory, ID):
        # Create the directory
        path = directory
        if os.path.exists(path) is False:
            os.mkdir(path)
            # print("Directory '% s' created" % directory)
        fig = plt.figure()
        self.visualize()
        fig.savefig(
            "{}/{}".format(directory, str(ID) + ".png"))

        # Starting point
        start_point = self.starting_point
        end_point = self.ending_point
        park_point = self.parking_point
        # for i in range(0, len(start_point) - 1):
        #     fn = os.path.dirname(os.path.realpath(__file__)) + "/data/" + directory + '/' + str(ID) + str(
        #         i + 1) + ".json"
        #     with open(fn, 'w') as fp:
        #         json.dump(
        #             {
        #                 "start": [start_point[i][0], start_point[i][1]],
        #                 "end": [end_point[i][0], end_point[i][1]]
        #             }
        #             , fp)

        # Export the center point only. Discard the 1st and 3rd.
        fn = directory + '/' + str(ID) + ".json"
        if self.parking_point is None:
            with open(fn, 'w') as fp:
                json.dump(
                    {
                        "start": [start_point[1][0], start_point[1][1]],
                        "end": [end_point[1][0], end_point[1][1]]
                    }
                    , fp)
        else:
            with open(fn, 'w') as fp:
                json.dump(
                    {
                        "start": [start_point[1][0], start_point[1][1]],
                        "end": [end_point[1][0], end_point[1][1]],
                        "park": [park_point[1][0], park_point[1][1]],
                    }
                    , fp)

    def visualize(self):
        # Oracle is the UNION of the AREAs OF THOSE LANELETS
        oracle_polygons = [self.predecessor.convert_to_polygon().shapely_object,
                           self.intersection.convert_to_polygon().shapely_object,
                           self.successor.convert_to_polygon().shapely_object]

        postiv_path = (self.predecessor, self.intersection, self.successor)
        # print("PATH:", [l.lanelet_id for l in postiv_path])

        # Starting point
        start_point = self.starting_point
        end_point = self.ending_point
        park_point = self.parking_point

        for i in range(0, len(start_point) - 1):
            plt.plot(*start_point[i], "o")
            plt.plot(*end_point[i], "x")
            if park_point is not None:
                plt.plot(*park_point[1], "s")

        Common.plot_polygon(oracle_polygons[0])
        Common.plot_polygon(oracle_polygons[1])
        Common.plot_polygon(oracle_polygons[2])
        plt.gca().set_aspect('equal', 'box')
        # plt.show()

    def _compute_feature_vector(self):
        # Compute Feature Direction Coverage
        dc = direction_coverage(self.interpolated_points)

        # Compute feature Min Radius
        mr = min(min_radius(self.interpolated_points), 100)

        return {
            "feature_vector": [dc, mr],
            "dc": dc,
            "mr": mr
        }

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
