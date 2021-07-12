import os
import json
import shutil
from models import MapModel, Scenario, SimModel
from models.lanelet import LaneLet, Path


class Experiment:
    def __init__(self, maps, filter, name, plan) -> None:
        self.maps = maps
        self.filter = filter
        self.name = name
        self.plan = plan

    @staticmethod
    def _empty_data_folder():
        path = "{}/lanelet/data/".format(os.path.dirname(os.path.realpath(__file__)))
        shutil.rmtree(path)
        os.mkdir(path)

    @staticmethod
    def run_scenario(id, map):
        try:
            file_path = "{}/lanelet/data/{}/{}".format(os.path.dirname(os.path.realpath(__file__)),
                                                            map.value[0],
                                                            str(id) + ".json")
            with open(file_path) as file:
                scenario_data = json.load(file)
            scenario = Scenario(scenario_data["start"], scenario_data["end"], map, id)
            SimModel.run(scenario)
        except Exception as e:
            print("{}".format(e))

    def run(self):
        # Read the map and generate data files
        self._empty_data_folder()
        for map in self.maps:
            lanelet = LaneLet(map.value[2])
            path_model = Path(lanelet.intersections, lanelet.lanelet_network)
            paths = self.filter(path_model.generate_driving_paths())
            for i in range(0, len(paths)):
                paths[i].to_json(map.value[0], i)

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
                    scenario = Scenario(scenario_data["start"], scenario_data["end"], map, idx)
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
