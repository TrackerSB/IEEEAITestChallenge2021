from models import Experiment, Filter, MapModel
from models.plan import StraightModel, ParkingModel
import random

LEFT = -1.9
MIDDLE = 0
RIGHT = 1.9


# SCRIPT 1: Generate data path with different filter
def script_01():
    # MAPS = [MapModel.CubeTown, MapModel.BorregasAve, MapModel.Shalun, MapModel.SanFrancisco, MapModel.Gomentum]
    MAPS = [MapModel.CubeTown]
    # Create an instance of experiment
    expm = Experiment(maps=MAPS, name="My Experiment", plan=StraightModel)
    assert expm.generate_data_paths() == 12  # Generate all data paths
    expm.set_filter(Filter.compare_feature)  # Filter with Feature
    assert expm.generate_data_paths() == 5
    expm.set_filter(Filter.compare_distance)  # Filter with Distance
    assert expm.generate_data_paths() == 8


# SCRIPT 2: Execute a test case with Map CubeTown + Feature Filter
def script_02():
    expm = Experiment(maps=[MapModel.CubeTown], name="CubeTown Experiment", plan=StraightModel)
    expm.set_filter(Filter.compare_feature)
    num_paths = expm.generate_data_paths()
    expm.run_scenario(id=random.randint(0, num_paths-1), map=MapModel.CubeTown)

    expm.set_plan(ParkingModel)
    num_paths = expm.generate_data_paths()
    expm.run_scenario(id=random.randint(0, num_paths-1), map=MapModel.CubeTown, distance=LEFT)
    expm.run_scenario(id=random.randint(0, num_paths-1), map=MapModel.CubeTown, distance=MIDDLE)
    expm.run_scenario(id=random.randint(0, num_paths-1), map=MapModel.CubeTown, distance=RIGHT)


# SCRIPT 3: Execute a test case with Map BorregasAve + Distance Filter
def script_03():
    expm = Experiment(maps=[MapModel.BorregasAve], name="BorregasAve Experiment", plan=StraightModel)
    expm.set_filter(Filter.compare_distance)
    num_paths = expm.generate_data_paths()
    expm.run_scenario(id=random.randint(0, num_paths-1), map=MapModel.BorregasAve)

    expm.set_plan(ParkingModel)
    num_paths = expm.generate_data_paths()
    expm.run_scenario(id=random.randint(0, num_paths-1), map=MapModel.BorregasAve, distance=LEFT)
    expm.run_scenario(id=random.randint(0, num_paths-1), map=MapModel.BorregasAve, distance=MIDDLE)
    expm.run_scenario(id=random.randint(0, num_paths-1), map=MapModel.BorregasAve, distance=RIGHT)


if __name__ == "__main__":
    script_01()
    script_02()
    script_03()
