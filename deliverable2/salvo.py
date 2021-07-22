from models import Experiment
from models.plan import StraightModel, ParkingModel
import click
import random


@click.group()
def cli():
    pass


MAPS = {
    "BorregasAve": "maps/BorregasAve.xodr",
    "CubeTown": "maps/CubeTown.xodr",
    "AutonomouStuff": "maps/AutonomouStuff.xodr",
    "SanFrancisco": "maps/SanFrancisco.xodr",
    "Shalun": "maps/Shalun.xodr",
    "Gomentum": "maps/Gomentum.xodr"
}

DV_MAPS = {
    "BorregasAve": "Borregas Ave",
    "CubeTown": "Cubetown",
    "AutonomouStuff": "Autonomous Stuff",
    "SanFrancisco": "San Francisco",
    "Shalun": "Shalun",
    "Gomentum": "Gomentum"
}

SIDES = {
    "RIGHT": 0,
    "MIDDLE": 1,
    "LEFT": 2
}


@cli.command()
@click.option('--map-file',
              type=click.Choice(['SanFrancisco', 'Gomentum', 'CubeTown', 'BorregasAve', 'Shalun'], case_sensitive=True))
@click.option('--before-junction', type=int, help="Distance before entering junction")
@click.option('--after-junction', type=int, help="Distance after leaving junction")
@click.option('--filter', nargs=3, is_flag=False, flag_value="Flag", type=(str, float, bool),
              help="[Optional] Filter Arguments: Method (Distance or Feature), Measure (Min-distance or the number "
                   "of cells) and Display Plot or not")
def generate_all_paths(map_file, before_junction, after_junction, filter):
    map_list = MAPS[map_file].split('/')
    mmap = {
        "name": map_list[len(map_list) - 1].split('.')[0],
        "path": MAPS[map_file],
        "dv": DV_MAPS[map_file]
    }
    expm = Experiment(mmap=mmap, name="Generate All Possible Paths", plan=StraightModel)
    if filter is not None:
        method, value, show_plot = filter
        if method == "distance":
            expm.set_filter({"method": method, "distance": value, "show_plot": show_plot})
        if method == "feature":
            expm.set_filter({"method": method, "cells": value, "show_plot": show_plot})
    expm.generate_data_paths(before_junction, after_junction)


@cli.command()
@click.option('--map-file',
              type=click.Choice(['SanFrancisco', 'Gomentum', 'CubeTown', 'BorregasAve', 'Shalun'], case_sensitive=True))
@click.option('--before-junction', type=int, help="Distance before entering junction")
@click.option('--after-junction', type=int, help="Distance after leaving junction")
@click.option('--samples', type=int, help="How many tests to sample for Test Pools")
@click.option('--filter', nargs=3, is_flag=False, flag_value="Flag", type=(str, float, bool),
              help="[Optional] Filter Arguments: Method (Distance or Feature), Measure (Min-distance or the number "
                   "of cells) and Display Plot or not")
def run_scenarios(map_file, before_junction, after_junction, samples, filter):
    LEFT = -1.91
    MIDDLE = 0
    RIGHT = 1.91

    map_list = MAPS[map_file].split('/')
    mmap = {
        "name": map_list[len(map_list) - 1].split('.')[0],
        "path": MAPS[map_file],
        "dv": DV_MAPS[map_file]
    }
    expm = Experiment(mmap=mmap, name="Generate All Possible Paths", plan=StraightModel)
    if filter != () and filter[0] == "distance":
        expm.set_filter({"method": filter[0], "distance": float(filter[1]), "show_plot": filter[2]})
    if filter != () and filter[0] == "feature":
        expm.set_filter({"method": filter[0], "cells": float(filter[1]), "show_plot": filter[2]})

    for i in range(0, int(samples)):
        expm.set_plan(StraightModel)
        num_paths = expm.generate_data_paths(before_junction, after_junction)
        expm.run_scenario(id=random.randint(0, num_paths - 1))

        expm.set_plan(ParkingModel)
        num_paths = expm.generate_data_paths(before_junction, after_junction, 5)
        expm.run_scenario(id=random.randint(0, num_paths - 1), distance=LEFT)
        expm.run_scenario(id=random.randint(0, num_paths - 1), distance=MIDDLE)
        expm.run_scenario(id=random.randint(0, num_paths - 1), distance=RIGHT)


@cli.command()
@click.option('--map-file',
              type=click.Choice(['SanFrancisco', 'Gomentum', 'CubeTown', 'BorregasAve', 'Shalun'], case_sensitive=True))
@click.option('--before-junction', type=int, help="Distance before entering junction")
@click.option('--after-junction', type=int, help="Distance after leaving junction")
@click.option('--parking-distance', type=int, help="Parking distance before entering junction")
@click.option('--parking-side', type=click.Choice(['LEFT', 'MIDDLE', 'RIGHT'], case_sensitive=True), is_flag=False, flag_value="Flag")
@click.option('--filter', nargs=3, is_flag=False, flag_value="Flag", type=(str, float, bool),
              help="[Optional] Filter Arguments: Method (Distance or Feature), Measure (Min-distance or the number "
                   "of cells) and Display Plot or not")
def generate_all_paths_with_parking(map_file, before_junction, after_junction, parking_distance, parking_side, filter):
    map_list = MAPS[map_file].split('/')
    mmap = {
        "name": map_list[len(map_list) - 1].split('.')[0],
        "path": MAPS[map_file],
        "dv": DV_MAPS[map_file]
    }
    if parking_side is None:
        parking_side = SIDES["RIGHT"]
    else:
        parking_side = SIDES[parking_side]
    expm = Experiment(mmap=mmap, name="Generate All Possible Paths", plan=ParkingModel)
    if filter is not None:
        method, value, show_plot = filter
        if method == "distance":
            expm.set_filter({"method": method, "distance": value, "show_plot": show_plot})
        if method == "feature":
            expm.set_filter({"method": method, "cells": value, "show_plot": show_plot})
    expm.generate_data_paths(before_junction, after_junction, parking_distance, parking_side)


@cli.command()
@click.option('--map-file',
              type=click.Choice(['SanFrancisco', 'Gomentum', 'CubeTown', 'BorregasAve', 'Shalun'], case_sensitive=True))
@click.option('--id', type=int, help="ID of a scenario in the data/map-file we want to execute")
@click.option('--plan-type', type=click.Choice(['nonNPC', 'NPC'], case_sensitive=True))
def run_scenario_by_id(map_file, id, plan_type):
    map_list = MAPS[map_file].split('/')
    mmap = {
        "name": map_list[len(map_list) - 1].split('.')[0],
        "path": MAPS[map_file],
        "dv": DV_MAPS[map_file]
    }
    if plan_type == 'nonNPC':
        expm = Experiment(mmap=mmap, name="Generate All Possible Paths", plan=StraightModel)
    else:
        expm = Experiment(mmap=mmap, name="Generate All Possible Paths", plan=ParkingModel)
    expm.run_scenario(id=id)


if __name__ == "__main__":
    cli()
