import os
import json
from lanelet import LaneLet, Path
from models import SimModel, MapModel, Scenario


def generate_data():
    for map in [MapModel.CubeTown, MapModel.BorregasAve, MapModel.AutonomouStuff]:
        lanelet = LaneLet(map.value[2])
        path_model = Path(lanelet.intersections, lanelet.lanelet_network)
        for intersection in lanelet.intersections:
            path_model.generate_driving_paths(intersection, map.value[0])


if __name__ == "__main__":
    # Read data file and execute simulation
    for map in [MapModel.CubeTown, MapModel.BorregasAve, MapModel.AutonomouStuff]:
        directory = map.value[0]
        ID = 1
        while True:
            try:
                file_path = "{}/lanelet/data/{}/{}".format(os.path.dirname(os.path.realpath(__file__)), directory,
                                                           str(ID) + ".json")
                with open(file_path) as file:
                    scenario_data = json.load(file)
                scenario = Scenario(scenario_data["start"], scenario_data["end"])
                SimModel.run(scenario, map)
                ID += 1
            except Exception as e:
                print(e)
                break