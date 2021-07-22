import os
import json
import shutil
from .lanelet import LaneLet, Path
from .scenario import Scenario
from .plan import ParkingModel
from .filter import Filter


class Experiment:
    def __init__(self, mmap, name, plan) -> None:
        self.mmap = mmap
        self.name = name
        self.plan = plan
        self.filter = None

    def set_plan(self, plan):
        self.plan = plan

    def set_filter(self, filter):
        self.filter = filter

    @staticmethod
    def _empty_data_folder():
        path = "data/"
        shutil.rmtree(path)
        os.mkdir(path)

    def run_scenario(self, id, distance=None):
        try:
            file_path = "data/" + self.mmap["name"] + '/' + str(id) + ".json"
            with open(file_path) as file:
                scenario_data = json.load(file)
            if self.plan.__name__ == "StraightModel":
                scenario = Scenario(start=scenario_data["start"],
                                    end=scenario_data["end"],
                                    mmap=self.mmap["name"],
                                    dvmap=self.mmap["dv"],
                                    tc_id=id)
                self.plan.run(scenario)
            else:
                scenario = Scenario(start=scenario_data["start"],
                                    end=scenario_data["end"],
                                    mmap=self.mmap["name"],
                                    tc_id=id,
                                    dvmap=self.mmap["dv"],
                                    park=scenario_data["park"],
                                    side=scenario_data["side"])
                p = ParkingModel()
                p.run(scenario=scenario, distance=distance)
        except Exception as e:
            print("{}".format(e))

    def generate_data_paths(self, before_junction, after_junction, parking_distance=0, side=0):
        if self.plan is None:
            raise Exception("Test Type (Go Straight or Parking) is not specified!")

        # Read the map and generate data files
        self._empty_data_folder()
        num_paths = 0

        # Generate Path Model
        lanelet = LaneLet(self.mmap["path"])
        if self.plan.__name__ == "StraightModel":
            path_model = Path(intersections=lanelet.intersections, lanelet_network=lanelet.lanelet_network,
                              before_entering_junction=before_junction, after_leaving_junction=after_junction)
            routes = path_model.generate_driving_paths()
        else:
            path_model = Path(intersections=lanelet.intersections,
                              lanelet_network=lanelet.lanelet_network,
                              before_entering_junction=before_junction, after_leaving_junction=after_junction,
                              before_entering_junction_parking=parking_distance)
            routes = path_model.generate_driving_paths_with_parking(side)

        # Filter the list of paths
        paths = 0
        if self.filter is not None:
            if self.filter["method"] == "distance":
                paths = Filter.compare_distance(routes, {"distance": self.filter["distance"], "show_plot": self.filter["show_plot"]})
            if self.filter["method"] == "feature":
                paths = Filter.compare_feature(routes, {"cells": int(self.filter["cells"]), "show_plot": self.filter["show_plot"]})
        else:
            paths = routes

        # Write the path to json files
        for i in range(0, len(paths)):
            paths[i].to_json(directory="data/{}".format(self.mmap["name"]), ID=i)
            num_paths += 1
        return num_paths


