import os
from .common import Common
from lxml import etree
from opendrive2lanelet.opendriveparser.elements.roadPlanView import PlanView
from opendrive2lanelet.opendriveparser.parser import parse_opendrive
from opendrive2lanelet.network import Network
from commonroad.scenario.lanelet import Lanelet


class LaneLet:
    def __init__(self, map_file="cubetown.xodr"):
        self.lanelet_network = None
        self.intersections = self.generate_intersections(map_file)

    def generate_intersections(self, map_file):
        PlanView.calc_geometry = Common.calc_geometry_patched
        Network.export_commonroad_scenario = Common.export_commonroad_scenario

        # Import, parse and convert OpenDRIVE file
        map_file = map_file

        with open("{}/maps/{}".format(os.path.dirname(os.path.realpath(__file__)), map_file), "r") as fi:
            open_drive = parse_opendrive(etree.parse(fi).getroot())

        road_network = Network()
        road_network.load_opendrive(open_drive)

        # Load this so the numbers are exactly the same in the GUI for manual inspection
        scenario = road_network.export_commonroad_scenario()
        # Access the underlying lanelet network
        self.lanelet_network = scenario.lanelet_network

        # Extend the definition of the Lanelet object to ease our analysis
        def has_no_relation_with(self, another_lanelet):
            return self.lanelet_id not in (another_lanelet.successor + another_lanelet.predecessor) or \
                   self.lanelet_id != another_lanelet.adj_left or \
                   self.lanelet_id != another_lanelet.adj_right or \
                   self.lanelet_id != l2.adj_left_same_direction or \
                   self.lanelet_id != l2.adj_right_same_direction

        Lanelet.has_no_relation_with = has_no_relation_with
        Lanelet.interpolate_position_any = Common.interpolate_position_any

        # TODO This changes only the instances but at the moment I have no idea how to handle this at class level...
        # Probably it would be enought to extend the class instead of dynamically modify its instances
        for lanelet in self.lanelet_network.lanelets:
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
        for l1, l2 in Common.all_different_pairs([lanelet for lanelet in self.lanelet_network.lanelets]):

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


        # Initialize and then merge all the groups of lanelets that have shared items
        intersections = list()
        for lanelet in self.lanelet_network.lanelets:
            if len(lanelet.overlaps) > 0:
                lanelet_together = set()
                lanelet_together.add(lanelet.lanelet_id)
                lanelet_together.update(list(lanelet.overlaps))
                intersections.append(lanelet_together)

        # Formulation one. It contains some spurious lanelets
        # try to clean up
        intersections = list(Common.connected_components(intersections))

        for intersection in intersections:
            print("Processing", intersection)
            # Iterate over a copy
            for lanelet_id in intersection[:]:
                # if the lanelets has adj lanelets but those do not belong to the intersection flag that
                lanelet = self.lanelet_network.find_lanelet_by_id(lanelet_id)
                adjacents = list()
                if lanelet.adj_right:
                    adjacents.append(lanelet.adj_right)
                if lanelet.adj_left:
                    adjacents.append(lanelet.adj_left)

                adjacent_inside_intersection = [a for a in adjacents if a not in intersection]
                if len(adjacent_inside_intersection) > 0:
                    intersection.remove(lanelet_id)

        return intersections
