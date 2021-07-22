import math
from .route import Route

MIDDLE = 0
RIGHT = 1
LEFT = 2


class Path:
    def __init__(self, intersections, lanelet_network, before_entering_junction=20, after_leaving_junction=20,
                 interpolate_every=2, before_entering_junction_parking=0):
        self.intersections = intersections
        self.lanelet_network = lanelet_network
        self.before_entering_junction = before_entering_junction
        self.after_leaving_junction = after_leaving_junction
        self.interpolate_every = interpolate_every
        self.before_entering_junction_parking = before_entering_junction_parking
        self.max_distance_before_entering_junction = 0
        self.max_distance_after_leaving_junction = 0


    def generate_junction_points(self, predecessor_lanelet, lanelet_inside_intersection, successor_lanelet):
        predecessor_lanelet_length = predecessor_lanelet.distance[-1]
        # assert predecessor_lanelet_length - self.max_distance_before_entering_junction > 0
        # Compute how many samples we can fit there
        n_points = math.floor(self.max_distance_before_entering_junction / self.interpolate_every)
        predecessor_points = [
            predecessor_lanelet.interpolate_position_any(
                -self.max_distance_before_entering_junction + p * self.interpolate_every, 
                positive_direction_at_zero = False)[0] for p in 
            range(0, n_points + 1)]

        # Consider the points within the junction
        shift_by = self.interpolate_every - (
                self.max_distance_before_entering_junction - (n_points * self.interpolate_every))
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
        # assert successor_lanelet_length - self.max_distance_after_leaving_junction > 0
        n_points = math.floor((self.max_distance_after_leaving_junction - shift_by) / self.interpolate_every)
        successor_points = [successor_lanelet.interpolate_position_any(p * self.interpolate_every + shift_by)[0] 
                            for 
                            p in range(0, n_points + 1)]

        return {
            "predecessor_points": predecessor_points,
            "inside_points": inside_points,
            "successor_points": successor_points
        }

    def generate_driving_paths(self):
        routes = list()
        for intersection in self.intersections:
            for lanelet_inside_intersection_id in intersection:
                lanelet_inside_intersection = self.lanelet_network.find_lanelet_by_id(lanelet_inside_intersection_id)

                if len(lanelet_inside_intersection.predecessor) != 1 or len(lanelet_inside_intersection.successor) != 1:
                    print("Unexpected element in the intersection. Skip it")
                    continue

                predecessor_lanelet = self.lanelet_network.find_lanelet_by_id(lanelet_inside_intersection.predecessor[0])
                successor_lanelet = self.lanelet_network.find_lanelet_by_id(lanelet_inside_intersection.successor[0])

                # ALESSIO: Ensure we do not overflow
                self.max_distance_before_entering_junction = self.before_entering_junction \
                    if predecessor_lanelet.distance[-1] > self.before_entering_junction else predecessor_lanelet.distance[-1]

                self.max_distance_after_leaving_junction = self.after_leaving_junction \
                    if successor_lanelet.distance[-1] > self.after_leaving_junction else successor_lanelet.distance[-1]

                # Starting and Ending point
                starting_point = predecessor_lanelet.interpolate_position_any(-self.max_distance_before_entering_junction)
                ending_point = successor_lanelet.interpolate_position_any(self.max_distance_after_leaving_junction)
                jp_dict = self.generate_junction_points(predecessor_lanelet, lanelet_inside_intersection, successor_lanelet)
                predecessor_points, inside_points, successor_points = jp_dict.values()

                # Interpolated path.
                # TODO This may require some love
                interpolated_path = list()
                interpolated_path.extend(predecessor_points)
                interpolated_path.extend(inside_points)
                interpolated_path.extend(successor_points)

                # Make sure we keep track of it
                route = Route(predecessor=predecessor_lanelet,
                              intersection=lanelet_inside_intersection,
                              successor=successor_lanelet,
                              starting_point=starting_point,
                              ending_point=ending_point,
                              interpolated_points=[(p[0], p[1]) for p in interpolated_path])

                routes.append(route)
                # route.visualize()

        return routes

    def generate_driving_paths_with_parking(self, side=0):
        routes = list()
        for intersection in self.intersections:
            for lanelet_inside_intersection_id in intersection:
                lanelet_inside_intersection = self.lanelet_network.find_lanelet_by_id(
                    lanelet_inside_intersection_id)

                if len(lanelet_inside_intersection.predecessor) != 1 or len(
                        lanelet_inside_intersection.successor) != 1:
                    print("Unexpected element in the intersection. Skip it")
                    continue

                predecessor_lanelet = self.lanelet_network.find_lanelet_by_id(
                    lanelet_inside_intersection.predecessor[0])
                successor_lanelet = self.lanelet_network.find_lanelet_by_id(
                    lanelet_inside_intersection.successor[0])

                # ALESSIO: Ensure we do not overflow
                self.max_distance_before_entering_junction = self.before_entering_junction \
                    if predecessor_lanelet.distance[-1] > self.before_entering_junction else predecessor_lanelet.distance[-1]

                self.max_distance_after_leaving_junction = self.after_leaving_junction \
                    if successor_lanelet.distance[-1] > self.after_leaving_junction else successor_lanelet.distance[-1]

                # Starting and Ending point
                starting_point = predecessor_lanelet.interpolate_position_any(-self.max_distance_before_entering_junction)
                ending_point = successor_lanelet.interpolate_position_any(self.max_distance_after_leaving_junction)
                parking_point = predecessor_lanelet.interpolate_position_any(-self.before_entering_junction_parking)
                jp_dict = self.generate_junction_points(predecessor_lanelet, lanelet_inside_intersection,
                                                        successor_lanelet)
                predecessor_points, inside_points, successor_points = jp_dict.values()

                # Interpolated path.
                # TODO This may require some love
                interpolated_path = list()
                interpolated_path.extend(predecessor_points)
                interpolated_path.extend(inside_points)
                interpolated_path.extend(successor_points)

                selected_parking_point = parking_point[RIGHT]
                if side == 1:
                    selected_parking_point = parking_point[MIDDLE]
                if side == 2:
                    selected_parking_point = parking_point[LEFT]

                # Make sure we keep track of it
                route = Route(predecessor=predecessor_lanelet,
                              intersection=lanelet_inside_intersection,
                              successor=successor_lanelet,
                              starting_point=starting_point,
                              ending_point=ending_point,
                              interpolated_points=[(p[0], p[1]) for p in interpolated_path],
                              parking_point=selected_parking_point,
                              side=side)

                routes.append(route)
                # route.visualize()

        return routes
