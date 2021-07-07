import numpy as np
from commonroad.scenario.scenario import Scenario
from collections import defaultdict
import matplotlib.pyplot as plt


class Common:
    def calc_geometry_patched(self, s_pos: float):
        try:
            # get index of geometry which is at s_pos
            mask = self._geo_lengths > s_pos
            sub_idx = np.argmin(self._geo_lengths[mask] - s_pos)
            geo_idx = np.arange(self._geo_lengths.shape[0])[mask][sub_idx] - 1
        except ValueError:
            # s_pos is after last geometry because of rounding error
            if np.isclose(s_pos, self._geo_lengths[-1], rtol=1.e-1):
                geo_idx = self._geo_lengths.size - 2
            else:
                raise Exception(
                    f"Tried to calculate a position outside of the borders of the reference path at s={s_pos}"
                    f", but path has only length of l={self._geo_lengths[-1]}"
                )

        # geo_idx is index which geometry to use
        return self._geometries[geo_idx].calc_position(
            s_pos - self._geo_lengths[geo_idx]
        )

    def export_commonroad_scenario(self, dt: float = 0.1, benchmark_id=None, filter_types=None):
        scenario = Scenario(
            dt=dt, scenario_id=None, benchmark_id=benchmark_id if benchmark_id is not None else "none"
        )

        scenario.add_objects(
            self.export_lanelet_network(
                filter_types=filter_types
                if isinstance(filter_types, list)
                else ["driving", "onRamp", "offRamp", "exit", "entry"]
            )
        )

        return scenario

    @staticmethod
    def all_different_pairs(iterable):
        "s -> (s0, s1), (s0, s2), (s0, s3), ... (s1, s0), (s1, s2), ..."
        for e1 in iterable:
            for e2 in iterable:
                if e1 == e2:
                    continue
                yield e1, e2

    @staticmethod
    def connected_components(lists):
        neighbors = defaultdict(set)
        seen = set()
        for each in lists:
            for item in each:
                neighbors[item].update(each)

        def component(node, neighbors=neighbors, seen=seen, see=seen.add):
            nodes = set([node])
            next_node = nodes.pop
            while nodes:
                node = next_node()
                see(node)
                nodes |= neighbors[node] - seen
                yield node

        for node in neighbors:
            if node not in seen:
                yield sorted(component(node))

    def interpolate_position_any(self, distance: float, positive_direction_at_zero=True) -> tuple:
        max_distance = self.distance[-1]
        if np.equal(distance, 0):
            if positive_direction_at_zero:
                return self.interpolate_position(distance)
            else:
                return self.interpolate_position(max_distance)
        elif np.greater(distance, 0):

            # Make sure we cap to max distance so we do not trigger the error
            if np.greater(distance, max_distance):
                distance = max_distance

            return self.interpolate_position(distance)
        else:
            distance = max_distance + distance
            # Make sure we cap to max distance so we do not trigger the error
            assert np.greater(distance, 0)

            return self.interpolate_position(distance)

    @staticmethod
    def plot_polygon(poly):
        plt.plot(*poly.exterior.xy)

    @staticmethod
    def plot_line(points):
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        # Plot the points
        # x, y = the_points.T
        plt.gca().set_aspect('equal')
        plt.plot(x, y)
        max_x = max(x)
        min_x = min(x)
        max_y = max(y)
        min_y = min(y)
        plt.xlim([min_x - 10, max_x + 10])
        plt.ylim([min_y - 10, max_y + 10])