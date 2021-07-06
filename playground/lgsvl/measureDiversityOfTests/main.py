import os
from itertools import combinations
from lxml import etree
from queue import Queue
import math

import matplotlib.pyplot as plt
from opendrive2lanelet.opendriveparser.elements.roadPlanView import PlanView


def plot_polygon(poly):
    plt.plot(*poly.exterior.xy)


def all_different_pairs(iterable):
    "s -> (s0, s1), (s0, s2), (s0, s3), ... (s1, s0), (s1, s2), ..."
    for e1 in iterable:
        for e2 in iterable:
            if e1 == e2:
                continue
            yield e1, e2


#### PATCH PlanView
import numpy as np
# Modified version of the calc_geometry method. The mod is only: "rtol=1.e-1"
def calc_geometry_patched(self, s_pos: float):
    """Calc position and tangent at s_pos by delegating calculation to geometry.

    Args:
      s_pos: Position on PlanView in ds.

    Returns:
      Position (x,y) in cartesion coordinates.
      Angle in radians at position s_pos.

    """
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
                f", but path has only length of l={ self._geo_lengths[-1]}"
            )

    # geo_idx is index which geometry to use
    return self._geometries[geo_idx].calc_position(
        s_pos - self._geo_lengths[geo_idx]
    )
PlanView.calc_geometry = calc_geometry_patched

from opendrive2lanelet.opendriveparser.parser import parse_opendrive
from opendrive2lanelet.io.opendrive_convert import convert_opendrive
from opendrive2lanelet.network import Network
from commonroad.scenario.scenario import Scenario

#### PATCH NETWORK

def export_commonroad_scenario(self, dt: float = 0.1, benchmark_id=None, filter_types=None):
    """Export a full CommonRoad scenario

    Args:
      dt:  (Default value = 0.1)
      benchmark_id:  (Default value = None)
      filter_types:  (Default value = None)

    Returns:

    """

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

Network.export_commonroad_scenario = export_commonroad_scenario

# # Import, parse and convert OpenDRIVE file
map_file = "cubetown.xodr"
# map_file = "borregasave.xodr"

with open("{}/{}". format(os.path.dirname(os.path.realpath(__file__)), map_file), "r") as fi:
    open_drive = parse_opendrive(etree.parse(fi).getroot())

# Load and find all the paths
road_network = Network()
road_network.load_opendrive(open_drive)

# Load this so the numbers are exactly the same in the GUI for manual inspection
scenario = road_network.export_commonroad_scenario()
# Access the underlying lanelet network
lanelet_network = scenario.lanelet_network

# An heuristic is to include in a junction mergers and splitters, but this is not enoguh as in some cases
# one can only cross the junction straight, and that's no merger or splitter.
# A safer way is to check for overlapping areas: Somehow there's a junction if two lanes overlap, so we can group
# lanelets by overlapping relations (in addition to the others releations


splitters = list()
mergers = list()
enders = list()
starter = list()

# Extend the definition of the Lanelet object to ease our analysis
from commonroad.scenario.lanelet import Lanelet

def has_no_relation_with(self, another_lanelet):
    return self.lanelet_id not in ( another_lanelet.successor + another_lanelet.predecessor ) or \
        self.lanelet_id != another_lanelet.adj_left or \
        self.lanelet_id != another_lanelet.adj_right or \
        self.lanelet_id !=l2.adj_left_same_direction or \
        self.lanelet_id != l2.adj_right_same_direction


def interpolate_position_any(self, distance: float, positive_direction_at_zero = True) -> tuple:
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

Lanelet.has_no_relation_with = has_no_relation_with
Lanelet.interpolate_position_any = interpolate_position_any

# TODO This changes only the instances but at the moment I have no idea how to handle this at class level...
# Probably it would be enought to extend the class instead of dynamically modify its instances
for lanelet in lanelet_network.lanelets:
    setattr(lanelet, "overlaps", set())
    setattr(lanelet, "is_splitter", False)
    setattr(lanelet, "is_merger", False)
    setattr(lanelet, "is_ender", False)
    setattr(lanelet, "is_starter", False)
    #
    lanelet.is_ender = len(lanelet.successor) == 0
    lanelet.is_starter = len(lanelet.predecessor) == 0
    lanelet.is_splitter = len(lanelet.successor) > 1
    lanelet.is_merger = len(lanelet.predecessor) > 1

# Compute Overlaps
for l1, l2 in all_different_pairs([lanelet for lanelet in lanelet_network.lanelets]):

    # Overlaps with is reflexive but not transitive requires some heuristic to deal with invalid polygons
    if l1.lanelet_id not in l2.overlaps:

        p1 = l1.convert_to_polygon().shapely_object
        p2 = l2.convert_to_polygon().shapely_object

        if p1.overlaps(p2) and l1.has_no_relation_with(l2) and l2.has_no_relation_with(l1):
            # Some polygons are weird (just enable the plotting code to see, but can be fixed using a trick.
            # We do that here to define a tolerance value on the overlap. If the overlap is too small, we do not consider
            # the lanelets to overlap at all
            if not p1.is_valid:
                # Risky but for the moment the only option we have
                p1 = p1.buffer(0)

            if not p2.is_valid:
                # Risky but for the moment the only option we have
                p2 = p2.buffer(0)

            # If they do not overlap enough, they will not overlap also in the other case!
            overlapping_area_p1 = round(p1.intersection(p2).area / p1.area * 100, 3)
            overlapping_area_p2 = round(p2.intersection(p1).area / p2.area * 100, 3)

            # TODO I found this empirically, the issue is that the lanelets overlaps even if they should NOT
            #  so we need an heuristic
            if min(overlapping_area_p1, overlapping_area_p2) > 5.0:
                l1.overlaps.add(l2.lanelet_id)
                l2.overlaps.add(l1.lanelet_id)

from collections import defaultdict

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

# Initialize and then merge all the groups of lanelets that have shared items
intersections = list()
for lanelet in lanelet_network.lanelets:
    if len(lanelet.overlaps) > 0:
        lanelet_together = set()
        lanelet_together.add(lanelet.lanelet_id)
        lanelet_together.update(list(lanelet.overlaps))
        intersections.append(lanelet_together)

intersections = list(connected_components(intersections))

for intersection in intersections:
    # Iterate over a copy
    for lanelet_id in intersection[:]:
        # if the lanelets has adj lanelets but those do not belong to the intersection flag that
        lanelet = lanelet_network.find_lanelet_by_id(lanelet_id)
        adjacents = list()
        if lanelet.adj_right:
            adjacents.append(lanelet.adj_right)
        if lanelet.adj_left:
            adjacents.append(lanelet.adj_left)

        adjacent_inside_intersection = [a for a in adjacents if a not in intersection]

        if len(adjacent_inside_intersection) > 0:
            intersection.remove(lanelet_id)



def plot_points(points):
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    # Plot the points
    # x, y = the_points.T
    plt.gca().set_aspect('equal')
    # plt.scatter(x, y)
    plt.plot(x, y, "o")

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



#
# For each path we interpolate the central line of the lanelets by the INTERPOLATE_EVERY amount of meters. This sequence of points makes
# it easy to compute the edit distance between paths and the features
#
INTERPOLATE_EVERY = 2

# Meters *up to*
BEFORE_ENTERING_JUNCTION = 20
AFTER_LEAVING_JUNCTION = 20

# We need to start from the intersection and move back BEFORE_ENTERING_JUNCTION meters to find the starting point
# then interpolate the points across the three lanelets up to AFTER_LEAVING_JUNCTION meters after the intersection to
# find the ending points
positive_paths = list()
for intersection in intersections:
    for lanelet_inside_intersection_id in intersection:

        lanelet_inside_intersection = lanelet_network.find_lanelet_by_id(lanelet_inside_intersection_id)

        if len(lanelet_inside_intersection.predecessor) != 1 or len(lanelet_inside_intersection.successor) != 1:
            print("Unexpected element in the intersection. Skip it")
            continue

        predecessor_lanelet = lanelet_network.find_lanelet_by_id(lanelet_inside_intersection.predecessor[0])
        successor_lanelet = lanelet_network.find_lanelet_by_id(lanelet_inside_intersection.successor[0])

        # Create an dictionary containing all the data
        positive_path = {
                            "predecessor": predecessor_lanelet,
                            "intersection": lanelet_inside_intersection,
                            "successor": successor_lanelet
        }

        # Make sure we keep track of it
        positive_paths.append(positive_path)

        # Fill the object with additional properties

        # Starting point
        starting_point = predecessor_lanelet.interpolate_position_any(-BEFORE_ENTERING_JUNCTION)
        positive_path["starting_point"] = starting_point

        ending_point = successor_lanelet.interpolate_position_any(AFTER_LEAVING_JUNCTION)
        positive_path["ending_point"] = ending_point

        # Refactor to a method
        # Interpolate the path for computing diversity and features
        the_points = list()
        # Find the portion of road before the junction
        predecessor_lanelet_length = predecessor_lanelet.distance[-1]

        # TODO If this is not true we need to update the code and replace occurrences of BEFORE_ENTERING_JUNCTION with
        #  a variable that contains the max road length
        assert predecessor_lanelet_length - BEFORE_ENTERING_JUNCTION > 0

        # Compute how many samples we can fit there
        n_points = math.floor(BEFORE_ENTERING_JUNCTION / INTERPOLATE_EVERY)
        # Find the samples
        predecessor_points = [predecessor_lanelet.interpolate_position_any(-BEFORE_ENTERING_JUNCTION + p * INTERPOLATE_EVERY, positive_direction_at_zero = False)[0] for p in range(0, n_points + 1)]

        # Debug plot
        # plot_polygon(predecessor_lanelet.convert_to_polygon().shapely_object)
        # plot_points(predecessor_points)

        # Check if there's some road left to cover in this lanelet
        shift_by = INTERPOLATE_EVERY - (BEFORE_ENTERING_JUNCTION - (n_points * INTERPOLATE_EVERY))
        # print("Shift points by", shift_by)

        # Do the "normal interpolation"
        n_points = math.floor((lanelet_inside_intersection.distance[-1] - shift_by) / INTERPOLATE_EVERY)
        #
        inside_points = [lanelet_inside_intersection.interpolate_position_any(p * INTERPOLATE_EVERY + shift_by)[0] for p in range(0, n_points + 1)]

        # Debug plot
        # plot_points(inside_points)
        # plot_polygon(lanelet_inside_intersection.convert_to_polygon().shapely_object)

        # Consider the points after the junction
        shift_by = INTERPOLATE_EVERY - (lanelet_inside_intersection.distance[-1] - (n_points * INTERPOLATE_EVERY + shift_by))
        # print("Shift next points by", shift_by)

        assert shift_by >= 0
        # TODO Alessio HERE!
        successor_lanelet_length = successor_lanelet.distance[-1]

        assert successor_lanelet_length - AFTER_LEAVING_JUNCTION > 0

        n_points = math.floor((AFTER_LEAVING_JUNCTION - shift_by) / INTERPOLATE_EVERY)
        #
        successor_points = [successor_lanelet.interpolate_position_any(p * INTERPOLATE_EVERY + shift_by)[0] for p in range(0, n_points + 1)]

        # Debug plot
        # plot_points(successor_points)
        # plot_polygon(successor_lanelet.convert_to_polygon().shapely_object)

        # Interpolated path.
        # TODO This may require some love
        interpolated_path = list()
        interpolated_path.extend(predecessor_points)
        interpolated_path.extend(inside_points)
        interpolated_path.extend(successor_points)

        positive_path["interpolated_path"] = [(p[0], p[1]) for p in interpolated_path]

        # plt.show()

# Compute input features for all the positive paths
from core.utils import direction_coverage, min_radius, count_turns
from core.utils import _pairwise as pairs
from self_driving.edit_distance_polyline import iterative_levenshtein, _standardize
from illumination.illumination_map import IlluminationMap, IlluminationAxisDefinition
from scipy.spatial.distance import cosine

# Compute the features for all the paths and store min/max values for each feature
# Use only 2 Features
dc_extrema = [math.inf, -math.inf]
mr_extrema = [math.inf, -math.inf]
#ct_extrema = [math.inf, -math.inf]

for p_path in positive_paths:
    interpolated_path = p_path["interpolated_path"]
    dc = direction_coverage(interpolated_path)
    dc_extrema[0] = min(dc_extrema[0], dc)
    dc_extrema[1] = max(dc_extrema[1], dc)

    # 100 means almost straight
    mr = min(min_radius(interpolated_path), 100)
    mr_extrema[0] = min(mr_extrema[0], mr)
    mr_extrema[1] = max(mr_extrema[1], mr)

    # Not sure this matters too much...
    # ct = count_turns(interpolated_path)
    # ct_extrema[0] = min(ct_extrema[0], ct)
    # ct_extrema[1] = max(ct_extrema[1], ct)

    # p_path["feature_vector"] = [dc, mr, ct]
    p_path["feature_vector"] = [dc, mr]
    p_path["dc"] = dc
    p_path["mr"] = mr

# Create the feature map - TODO Values needs some adjustment
direction_coverage_feature = IlluminationAxisDefinition("dc", dc_extrema[0], dc_extrema[1], 10)
min_radius_feature = IlluminationAxisDefinition("mr", mr_extrema[0], mr_extrema[1], 10)

illumination_map = IlluminationMap(direction_coverage_feature, min_radius_feature)

for sample in positive_paths:
    # Try to add the element to the map
    if illumination_map.is_cell_free(sample):
        print("NEW VALUE. ADD TO MAP")
    else:
        print("DISCARD VALUE. ALREADY IN MAP")
    illumination_map.add_sample(sample)

illumination_map.visualize()
plt.show()

for a, b in pairs(positive_paths):
    it_dist = iterative_levenshtein(a["interpolated_path"], b["interpolated_path"])

    # This is bounded 0 - 1
    # This seems quite sensitive with only 3 dimensions
    # TODO Probably this cosine similarity may work better if we rescale the vectors
    cosine_similarity = 1 - cosine(a["feature_vector"], b["feature_vector"])

    print("Comparing ", a["feature_vector"], "-", b["feature_vector"])

    # Plot only the roads that are too similar
    if it_dist < 2.0 or True:
        # Plot the standardized roads not the original one (they all start at (0,0))
        std_a = _standardize(a["interpolated_path"])
        std_b = _standardize(b["interpolated_path"])
        plot_points(std_a)
        plot_points(std_b)
        plt.title("IT Distance {} - Cosine Similarity {}".format(it_dist, cosine_similarity))
        plt.show()

    # if cosine_similarity > 0.9:
    #     # Plot the standardized roads not the original one (they all start at (0,0))
    #     std_a = _standardize(a["interpolated_path"])
    #     std_b = _standardize(b["interpolated_path"])
    #     plot_points(std_a)
    #     plot_points(std_b)
    #     plt.title("IT Distance {} - Cosine Similarity {}".format(it_dist, cosine_similarity))
    #     plt.show()

# for p_path in positive_paths:
#     interpolated_path = p_path["interpolated_path"]
#     dc = direction_coverage(interpolated_path)
#     mr = min_radius(interpolated_path)
#     ct = count_turns(interpolated_path)
#     # Convert to expected representation
#     # print("Features ")
#     # print("Direction coverage ", dc)
#     # print("Min Radius:", mr)
#     # print("Count segments/turns:", ct)
#
#     plot_points( interpolated_path )
#     plot_line(interpolated_path)
#     plt.title("Features: Dir Cov {} - Min Rad {} - Turn Count {} ".format(dc, mr, ct))
#     plt.show()

# Compute Edit Distance between pairs
