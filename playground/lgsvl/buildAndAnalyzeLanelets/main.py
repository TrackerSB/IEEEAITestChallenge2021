import os
from itertools import combinations
from lxml import etree

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
map_file = "cubetown.xodr"
# map_file = "autonomoustuff.xodr"
# map_file = "borregasave.xodr"
with open("{}/{}". format(os.path.dirname(os.path.realpath(__file__)), map_file), "r") as fi:
    open_drive = parse_opendrive(etree.parse(fi).getroot())

road_network = Network()
road_network.load_opendrive(open_drive)

# Load this so the numbers are exactly the same in the GUI for manual inspection
scenario = road_network.export_commonroad_scenario()
# Access the underlying lanelet network
lanelet_network = scenario.lanelet_network

# TODO     # Merge cells that have overlapping bounding boxes
#     merged_cells = cascaded_union([grid_cells[pos] for pos in idx.intersection(poly.bounds)])
# This for defining the oracle

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

# Extend the definition of this object
for lanelet in lanelet_network.lanelets:
    setattr(lanelet, "intersect", list())
    setattr(lanelet, "is_splitter", False)
    setattr(lanelet, "is_merger", False)
    setattr(lanelet, "is_ender", False)
    setattr(lanelet, "is_starter", False)
    lanelet.adj_left_same_direction
    lanelet.adj_right_same_direction

import matplotlib.pyplot as plt

# Find all the (partially) overlapping lanelets
# TODO Probably there's non need to check all pairs in both direction
for l1, l2 in all_different_pairs(lanelet_network.lanelets):
    # Overlaps with is reflexive but not transitive
    if l1.lanelet_id not in l2.intersect:
        p1 = l1.convert_to_polygon().shapely_object
        p2 = l2.convert_to_polygon().shapely_object

        if l1.convert_to_polygon().shapely_object.overlaps(l2.convert_to_polygon().shapely_object) and \
            (
                    # TODO Convert in a method
                    l1.lanelet_id not in ( l2.successor + l2.predecessor + [l2.adj_left] + [l2.adj_right] + [l2.adj_left_same_direction] + [l2.adj_right_same_direction]) or
                    l2.lanelet_id not in ( l1.successor + l1.predecessor + [l1.adj_left] + [l1.adj_right] + [l1.adj_left_same_direction] + [l1.adj_right_same_direction])
            ):

            # Some polygons are weird (just enable the plotting code to see, but can be fixed using a trick.
            # We do that here to define a tolerance value on the overlap. If the overlap is too small, we do not consider
            # the lanelets to overlap at all
            #

            if not p1.is_valid:
                # plt.clf()
                # print(l1, "NOT VALID")
                # plt.plot(*p1.exterior.xy)
                #
                # p1_fixed = p1.buffer(0)
                # plt.plot(*p1_fixed.exterior.xy)
                # Risky but for the moment the only option we have
                p1 = p1.buffer(0)

            if not p2.is_valid:
                # plt.clf()
                # print(l2, "NOT VALID")
                # plt.plot(*p2.exterior.xy)
                #
                # p2_fixed = p2.buffer(0)
                # plt.plot(*p2_fixed.exterior.xy)
                #
                # p2 = p2_fixed
                p2 = p2.buffer(0)

            # If they do not overlap enough, they will not overlap also in the other case!
            overlapping_area_p1 = p1.intersection(p2).area / p1.area * 100

            if overlapping_area_p1 > 1.0:
                print(l1, "overlaps with", l2)
                l1.intersect.append(l2.lanelet_id)
                l2.intersect.append(l1.lanelet_id)
    else:
        print(l1, "ALREADY overlaps with", l2)

    ###
    l1.is_ender = len(lanelet.successor) == 0
    l1.is_starter = len(lanelet.predecessor) == 0
    l1.is_splitter = len(lanelet.successor) > 1
    l1.is_merger = len(lanelet.predecessor) > 1