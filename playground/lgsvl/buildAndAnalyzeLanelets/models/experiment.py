import os
import json
import shutil
from models import MapModel, Scenario, SimModel
from models.lanelet import LaneLet, Path


class Experiment:
    def __init__(self, maps: list[MapModel], filter) -> None:
        self.maps = maps
        self.filter = filter

    @staticmethod
    def _empty_data_folder():
        path = "{}/lanelet/data/".format(os.path.dirname(os.path.realpath(__file__)))
        shutil.rmtree(path)
        os.mkdir(path)

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
                SimModel.run(tc)
            except Exception as e:
                failed_test_cases.append(tc)
                pass
                # print("{}".format(e))

        print(f'RESULT: {len(failed_test_cases)}/{len(test_cases)} FAILED!')