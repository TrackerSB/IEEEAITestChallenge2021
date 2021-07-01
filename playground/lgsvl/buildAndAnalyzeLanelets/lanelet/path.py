import matplotlib.pyplot as plt


def plot_polygon(poly):
    plt.plot(*poly.exterior.xy)


class Path:
    def __init__(self, intersections, lanelet_network):
        self.intersections = intersections
        self.lanelet_network = lanelet_network

    def generate_driving_paths(self, intersection, start_point_distance=0, end_point_distance=0):
        # Generate POSITIVE driving paths
        positive_driving_paths_across_intersections = list()
        for lanelet_inside_intersection_id in intersection:
            lanelet_inside_intersection = self.lanelet_network.find_lanelet_by_id(lanelet_inside_intersection_id)

            if len(lanelet_inside_intersection.predecessor) != 1 or len(lanelet_inside_intersection.successor) != 1:
                print("Unexpected element in the intersection. Skip it")
                continue

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

            plot_polygon(oracle_polygons[0])  # predecessor
            plot_polygon(oracle_polygons[1])  # intersection
            plot_polygon(oracle_polygons[2])  # successor

            plt.plot(*start_point[0], "o")
            plt.plot(*end_point[0], "x")

            plt.show()

            positive_driving_paths_across_intersections.append((start_point[0], end_point[0]))
        return positive_driving_paths_across_intersections
