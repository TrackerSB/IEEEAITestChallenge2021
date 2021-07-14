import os
import json
import shutil
from .lanelet import LaneLet, Path
from .scenario import Scenario
from .plan import ParkingModel


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

    def run_scenario(self, id, map, distance=None):
        try:
            file_path = "{}/lanelet/data/{}/{}".format(os.path.dirname(os.path.realpath(__file__)),
                                                       map.value[0],
                                                       str(id) + ".json")
            with open(file_path) as file:
                scenario_data = json.load(file)
            if self.plan.__name__ == "StraightModel":
                scenario = Scenario(start=scenario_data["start"],
                                    end=scenario_data["end"],
                                    mmap=map,
                                    tc_id=id)
                self.plan.run(scenario)
            else:
                scenario = Scenario(start=scenario_data["start"],
                                    end=scenario_data["end"],
                                    mmap=map,
                                    tc_id=id,
                                    park=scenario_data["park"])
                p = ParkingModel()
                p.set_distance(distance)
                p.run(scenario)
        except Exception as e:
            print("{}".format(e))

    def generate_data_paths(self, before_junction, after_junction, parking_distance=0):
        if self.plan is None:
            raise Exception("Test Type (Go Straight or Parking) is not specified!")

        # Read the map and generate data files
        self._empty_data_folder()
        num_paths = 0

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
            routes = path_model.generate_driving_paths_with_parking()
        if self.filter is not None:
            paths = self.filter(routes)
        else:
            paths = routes

        # Write the path to json files
        for i in range(0, len(paths)):
            paths[i].to_json(directory="data/{}".format(self.mmap["name"]), ID=i)
            num_paths += 1
        return num_paths

    def run(self):
        # Read the map and generate data files
        self.generate_data_paths()

        # Read data file and generate test cases
        test_cases = list()
        for map in self.maps:
            idx = 0
            while True:
                try:
                    file_path = "{}/lanelet/data/{}/{}".format(os.path.dirname(os.path.realpath(__file__)),
                                                               map.value[0],
                                                               str(idx) + ".json")
                    with open(file_path) as file:
                        scenario_data = json.load(file)
                    if self.plan.__name__ == "StraightModel":
                        scenario = Scenario(start=scenario_data["start"],
                                            end=scenario_data["end"],
                                            mmap=map,
                                            tc_id=idx)
                    else:
                        scenario = Scenario(start=scenario_data["start"],
                                            end=scenario_data["end"],
                                            mmap=map,
                                            tc_id=idx,
                                            park=scenario_data["park"])
                    test_cases.append(scenario)
                    idx += 1
                except Exception as e:
                    break
                    # print("{}".format(e))

        # Run test cases
        failed_test_cases = list()
        for tc in test_cases:
            try:
                self.plan.run(tc)
            except Exception as e:
                failed_test_cases.append(tc)
                pass
                # print("{}".format(e))

        print(f'{self.name.upper()} RESULT: {len(failed_test_cases)}/{len(test_cases)} FAILED!\n')
