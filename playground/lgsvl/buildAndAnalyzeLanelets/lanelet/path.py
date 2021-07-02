import os
import json
import shutil

import matplotlib.pyplot as plt


def plot_polygon(poly):
    plt.plot(*poly.exterior.xy)


class Path:
    def __init__(self, intersections, lanelet_network):
        self.intersections = intersections
        self.lanelet_network = lanelet_network

    def generate_driving_paths(self, intersection, directory,
                               start_point_distance=0, end_point_distance=0):

        # Create the directory
        path = "{}/data/{}".format(os.path.dirname(os.path.realpath(__file__)), directory)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        print("Directory '% s' created" % directory)

        # Generate POSITIVE driving paths
        positive_driving_paths_across_intersections = list()
        ID = 0
        for lanelet_inside_intersection_id in intersection:
            lanelet_inside_intersection = self.lanelet_network.find_lanelet_by_id(lanelet_inside_intersection_id)

            if len(lanelet_inside_intersection.predecessor) != 1 or len(lanelet_inside_intersection.successor) != 1:
                print("Unexpected element in the intersection. Skip it")
                continue

            ID += 1
            predecessor_lanelet = self.lanelet_network.find_lanelet_by_id(lanelet_inside_intersection.predecessor[0])
            successor_lanelet = self.lanelet_network.find_lanelet_by_id(lanelet_inside_intersection.successor[0])

            # Oracle is the UNION of the AREAs OF THOSE LANELETS
            oracle_polygons = [predecessor_lanelet.convert_to_polygon().shapely_object,
                               lanelet_inside_intersection.convert_to_polygon().shapely_object,
                               successor_lanelet.convert_to_polygon().shapely_object]

            positive_path = (predecessor_lanelet, lanelet_inside_intersection, successor_lanelet)
            print("PATH:", [l.lanelet_id for l in positive_path])

            start_point = predecessor_lanelet.interpolate_position_any(start_point_distance)
            end_point = successor_lanelet.interpolate_position_any(end_point_distance)

            fig = plt.figure()
            plot_polygon(oracle_polygons[0])  # predecessor
            plot_polygon(oracle_polygons[1])  # intersection
            plot_polygon(oracle_polygons[2])  # successor

            plt.plot(*start_point[0], "o")
            plt.plot(*end_point[0], "x")

            plt.show()
            fig.savefig(
                "{}/data/{}/{}".format(os.path.dirname(os.path.realpath(__file__)), directory, str(ID) + ".png"))

            positive_driving_paths_across_intersections.append((start_point[0], end_point[0]))

            with open("{}/data/{}/{}".format(os.path.dirname(os.path.realpath(__file__)), directory, str(ID) + ".json"),
                      'w') as fp:
                json.dump(
                    {
                        "path": [l.lanelet_id for l in positive_path],
                        "start": [start_point[0][0], start_point[0][1]],
                        "end": [end_point[0][0], end_point[0][1]]
                    }
                    , fp)
        return positive_driving_paths_across_intersections
