import os
import json
import math
from .route import Route



class Path:
    def __init__(self, intersections, lanelet_network, before_entering_junction=20, after_leaving_junction=20,
                 interpolate_every=2):
        self.intersections = intersections
        self.lanelet_network = lanelet_network
        self.before_entering_junction = before_entering_junction
        self.after_leaving_junction = after_leaving_junction
        self.interpolate_every = interpolate_every

    def generate_junction_points(self, predecessor_lanelet, lanelet_inside_intersection, successor_lanelet):
        predecessor_lanelet_length = predecessor_lanelet.distance[-1]
        assert predecessor_lanelet_length - self.before_entering_junction > 0
        # Compute how many samples we can fit there
        n_points = math.floor(self.before_entering_junction / self.interpolate_every)
        predecessor_points = [
            predecessor_lanelet.interpolate_position_any(
                -self.before_entering_junction + p * self.interpolate_every,
                positive_direction_at_zero=False)[0] for p in
            range(0, n_points + 1)]

        # Consider the points within the junction
        shift_by = self.interpolate_every - (
                self.before_entering_junction - (n_points * self.interpolate_every))
        n_points = math.floor((lanelet_inside_intersection.distance[-1] - shift_by) / self.interpolate_every)
        inside_points = [
            lanelet_inside_intersection.interpolate_position_any(p * self.interpolate_every + shift_by)[0] for p
            in
            range(0, n_points + 1)]

        # Consider the points after the junction
        shift_by = self.interpolate_every - (
                lanelet_inside_intersection.distance[-1] - (n_points * self.interpolate_every + shift_by))
        assert shift_by >= 0
        successor_lanelet_length = successor_lanelet.distance[-1]
        assert successor_lanelet_length - self.after_leaving_junction > 0
        n_points = math.floor((self.after_leaving_junction - shift_by) / self.interpolate_every)
        successor_points = [successor_lanelet.interpolate_position_any(p * self.interpolate_every + shift_by)[0]
                            for
                            p in range(0, n_points + 1)]

        return {
            "predecessor_points": predecessor_points,
            "inside_points": inside_points,
            "successor_points": successor_points
        }

    def generate_driving_paths(self, directory):
        # Create the directory
        path = "{}/data/{}".format(os.path.dirname(os.path.realpath(__file__)), directory)
        if os.path.exists(path) is False:
            os.mkdir(path)
            print("Directory '% s' created" % directory)

        routes = list()
        for intersection in self.intersections:
            for lanelet_inside_intersection_id in intersection:
                lanelet_inside_intersection = self.lanelet_network.find_lanelet_by_id(lanelet_inside_intersection_id)

                if len(lanelet_inside_intersection.predecessor) != 1 or len(lanelet_inside_intersection.successor) != 1:
                    print("Unexpected element in the intersection. Skip it")
                    continue

                predecessor_lanelet = self.lanelet_network.find_lanelet_by_id(lanelet_inside_intersection.predecessor[0])
                successor_lanelet = self.lanelet_network.find_lanelet_by_id(lanelet_inside_intersection.successor[0])

                # Starting and Ending point
                starting_point = predecessor_lanelet.interpolate_position_any(-self.before_entering_junction)
                ending_point = successor_lanelet.interpolate_position_any(self.after_leaving_junction)
                jp_dict = self.generate_junction_points(predecessor_lanelet, lanelet_inside_intersection, successor_lanelet)
                predecessor_points, inside_points, successor_points = jp_dict.values()

                # Interpolated path.
                # TODO This may require some love
                interpolated_path = list()
                interpolated_path.extend(predecessor_points)
                interpolated_path.extend(inside_points)
                interpolated_path.extend(successor_points)

                # Make sure we keep track of it
                route = Route(predecessor_lanelet, lanelet_inside_intersection, successor_lanelet,
                                    starting_point, ending_point, [(p[0], p[1]) for p in interpolated_path])
                routes.append(route)
                route.visualize()
                exit()

        print(len(routes))
        return []
