import os
from itertools import combinations
from lxml import etree
from queue import Queue

import matplotlib.pyplot as plt
from opendrive2lanelet.opendriveparser.elements.roadPlanView import PlanView
def plot_polygon(poly):
    plt.plot(*poly.exterior.xy)


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

def export_commonroad_scenario(
        self, dt: float = 0.1, benchmark_id=None, filter_types=None
):
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
#Cubetown:
#[100, 103, 106, 111, 112, 115]
#[107, 108, 109, 110, 113, 114]
map_file = "cubetown.xodr"

# This has problems because somehow overlapping segments are NOT reported overlapping at all
# So there are segments missing
# - somehow 135 is considered not overlapping, but is contained entirely in its predecessor
#
# [102, 103, 106, 107, 114, 115, 120, 121, 122, 127]
# [116, 117, 118, 119] - Missing 135 and 138
# [123, 124, 125, 126, 136, 137]
# [139, 140, 141, 142, 147, 148]
# [150, 151, 153, 154, 160, 162, 163, 164]
# map_file = "autonomoustuff.xodr"

# This has some problems because FAKE overlaps seem to be bigger than expected
# Not sure if I missed something
# [101, 103, 105, 107, 108, 114, 115, 119, 120, 122, 123, 125, 131, 132, 134, 135]
# [136, 137, 138, 139, 140, 141, 147, 148, 149, 150, 151, 152]
# map_file = "borregasave.xodr"

with open("{}/{}". format(os.path.dirname(os.path.realpath(__file__)), map_file), "r") as fi:
    open_drive = parse_opendrive(etree.parse(fi).getroot())

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

def all_different_pairs(iterable):
    "s -> (s0, s1), (s0, s2), (s0, s3), ... (s1, s0), (s1, s2), ..."
    for e1 in iterable:
        for e2 in iterable:
            if e1 == e2:
                continue
            yield e1, e2

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


def interpolate_position_any(self, distance: float) -> tuple:
    max_distance = self.distance[-1]
    if np.greater_equal(distance, 0):

        # Make sure we cap to max distance so we do not trigger the error
        if np.greater(distance, max_distance):
            distance = max_distance

        return self.interpolate_position(distance)
    else:
        distance = max_distance + distance
        # Make sure we cap to max distance so we do not trigger the error
        if np.less_equal(distance, 0):
            distance = 0

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
                print(l1, "overlaps with", l2, "AREA", overlapping_area_p1, "--", overlapping_area_p2)
                l1.overlaps.add(l2.lanelet_id)
                l2.overlaps.add(l1.lanelet_id)
            else:
                print(l1, "FAKE OVERLAP WITH", l2, "AREA", overlapping_area_p1, "--", overlapping_area_p2)
    else:
        print(l1, "ALREADY overlaps with", l2)

# Given a lanelet tha belongs to an intersection, all the overlapping lanelets belong to the same intersection
# all the adj lanelets of lanelets that belong an intersection belong to the same intersection

# Now consider all the following roads:
# Succ(splitter)
# Pred(merger)
# Succ(ADJ_SAME_DIRECTION(splitter))
# Pred(ADJ_SAME_DIRECTION(merger))


# All the lanelets that overlap belong to the same intersection (may not be accurate)
# Intersections contains only mergers and splitters
# Intersection contains
# Worklist algorithm
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

# Formulation one. It contains some spurious lanelets
# try to clean up
intersections = list(connected_components(intersections))

for intersection in intersections:
    print("Processing", intersection)
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
        print("Not inside intersection", adjacent_inside_intersection)
        if len(adjacent_inside_intersection) > 0:
            print(lanelet, "should NOT be inside the intersection")
            intersection.remove(lanelet_id)

[print(i) for i in intersections]

from shapely.ops import cascaded_union


# Generate POSITIVE driving paths
positive_driving_paths_across_intersections = list()
for intersection in intersections:
    for lanelet_inside_intersection_id in intersection:

        lanelet_inside_intersection = lanelet_network.find_lanelet_by_id(lanelet_inside_intersection_id)

        if len(lanelet_inside_intersection.predecessor) != 1 or len(lanelet_inside_intersection.successor) != 1:
            print("Unexpected element in the intersection. Skip it")
            continue

        predecessor_lanelet = lanelet_network.find_lanelet_by_id(lanelet_inside_intersection.predecessor[0])
        successor_lanelet = lanelet_network.find_lanelet_by_id(lanelet_inside_intersection.successor[0])


        # Oracle is the UNION of the AREAs OF THOSE LANELETS
        oracle_polygons = [predecessor_lanelet.convert_to_polygon().shapely_object,
                    lanelet_inside_intersection.convert_to_polygon().shapely_object,
                    successor_lanelet.convert_to_polygon().shapely_object]

        positive_path = (predecessor_lanelet, lanelet_inside_intersection, successor_lanelet)
        print("PATH:", [ l.lanelet_id for l  in positive_path])

        position_1 = predecessor_lanelet.interpolate_position_any(-5)
        position_2 = predecessor_lanelet.interpolate_position_any(-10)
        position_3 = predecessor_lanelet.interpolate_position_any(-15)

        plot_polygon(oracle_polygons[0])
        plt.plot(*position_1[0], "o")
        plt.plot(*position_2[0], "o")
        plt.plot(*position_3[0], "o")

        a_position_1 = successor_lanelet.interpolate_position_any(0)
        a_position_2 = successor_lanelet.interpolate_position_any(5)
        a_position_3 = successor_lanelet.interpolate_position_any(10)

        plot_polygon(oracle_polygons[1])

        plot_polygon(oracle_polygons[2])
        plt.plot(*a_position_1[0], "o")
        plt.plot(*a_position_2[0], "o")
        plt.plot(*a_position_3[0], "o")

        positive_driving_paths_across_intersections.append((position_2[0], a_position_3[0]))

        # [plot_polygon(p) for p in polygons]
        # Not this can easily be a MULTIPOLIGON as lanelets may NOT overlap precisely
        # Computing the convexhull does not work...
        # oracle_polygon = cascaded_union(polygons)

        # lanelet_network.find_lanelet_by_id(lanelet_inside_intersection.predecessor[0]).convert_to_polygon().shapely_object
[print(p) for p in positive_driving_paths_across_intersections]
