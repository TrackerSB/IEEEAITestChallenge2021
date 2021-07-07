import os
import json
from lanelet import LaneLet, Path
from models import SimModel, MapModel, Scenario
from correlation import compare_feature, compare_distance


def generate_data():
    for map in [MapModel.CubeTown]:
        lanelet = LaneLet(map.value[2])
        path_model = Path(lanelet.intersections, lanelet.lanelet_network)
        paths = compare_distance(path_model.generate_driving_paths())
        for i in range(0, len(paths) - 1):
            paths[i].to_json(map.value[0], i)


if __name__ == "__main__":
    generate_data()
    # Read data file and execute simulation
    # for map in [MapModel.CubeTown, MapModel.BorregasAve]:
    #     directory = map.value[0]
    #     ID = 1
    #     while True:
    #         try:
    #             file_path = "{}/lanelet/data/{}/{}".format(os.path.dirname(os.path.realpath(__file__)), directory,
    #                                                        str(ID) + ".json")
    #             with open(file_path) as file:
    #                 scenario_data = json.load(file)
    #             scenario = Scenario(scenario_data["start"], scenario_data["end"])
    #             SimModel.run(scenario, map, "Test Case {}".format(ID))
    #             ID += 1
    #         except Exception as e:
    #             print(e)
    #             break
