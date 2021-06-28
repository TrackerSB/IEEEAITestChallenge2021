import os
from itertools import combinations
from lxml import etree
from queue import Queue

from opendrive2lanelet.opendriveparser.parser import parse_opendrive
from opendrive2lanelet.io.opendrive_convert import convert_opendrive

# from opendrive2lanelet.opendriveparser.elements.junction import Junction
# from opendrive2lanelet.opendriveparser.elements.road import Road
#
from opendrive2lanelet.network import Network
#
# from commonroad.common.file_writer import CommonRoadFileWriter, OverwriteExistingFile
# from commonroad.planning.planning_problem import PlanningProblemSet
# from commonroad.scenario.scenario import Tag
#
# # Import, parse and convert OpenDRIVE file
#Cubetown:
#[100, 103, 106, 111, 112, 115]
#[107, 108, 109, 110, 113, 114]
#map_file = "cubetown.xodr"

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
map_file = "borregasave.xodr"

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

Lanelet.has_no_relation_with = has_no_relation_with

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


