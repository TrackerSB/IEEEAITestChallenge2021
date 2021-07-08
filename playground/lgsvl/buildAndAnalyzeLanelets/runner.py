import json
import os

from models import MapModel, Scenario, SimModel, Filter
from models.lanelet import LaneLet, Path


def generate_data():
    for map in [MapModel.CubeTown, MapModel.BorregasAve]:
        lanelet = LaneLet(map.value[2])
        path_model = Path(lanelet.intersections, lanelet.lanelet_network)
        paths = Filter.compare_distance(path_model.generate_driving_paths())
        for i in range(0, len(paths)):
            paths[i].to_json(map.value[0], i)


if __name__ == "__main__":
    generate_data()
    # Read data file and generate test cases
    test_cases = list()
    for map in [MapModel.CubeTown, MapModel.BorregasAve]:
        ID = 0
        while True:
            try:
                file_path = "{}/models/lanelet/data/{}/{}".format(os.path.dirname(os.path.realpath(__file__)),
                                                                  map.value[0],
                                                                  str(ID) + ".json")
                with open(file_path) as file:
                    scenario_data = json.load(file)
                scenario = Scenario(scenario_data["start"], scenario_data["end"], map, ID)
                test_cases.append(scenario)
                ID += 1
            except Exception as e:
                break

    # Run test cases
    # for tc in test_cases:
    #     try:
    #         SimModel.run(tc)
    #     except Exception as e:
    #         print(e)
    #         break
