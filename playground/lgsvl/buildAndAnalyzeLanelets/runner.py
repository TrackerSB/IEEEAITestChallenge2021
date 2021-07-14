from models import Experiment, Filter, MapModel
from models.plan import StraightModel, ParkingModel
import click


@click.group()
def cli():
    pass


LEFT = -1.9
MIDDLE = 0
RIGHT = 1.9


@cli.command()
@click.argument('map_file', type=click.Path(exists=True))
@click.argument('before_junction', nargs=1)
@click.argument('after_junction', nargs=1)
@click.argument('filter', nargs=-1)
def generate_all_paths(map_file, before_junction, after_junction, filter):
    map_list = map_file.split('/')
    mmap = {
        "name": map_list[len(map_list) - 1].split('.')[0],
        "path": map_file
    }
    expm = Experiment(mmap=mmap, name="Generate All Possible Paths", plan=StraightModel)
    if filter != () and filter[0] == "distance":
        expm.set_filter({"method": filter[0], "distance": float(filter[1]), "show_plot": filter[2]})
    if filter != () and filter[0] == "feature":
        expm.set_filter({"method": filter[0], "cells": float(filter[1]), "show_plot": filter[2]})
    expm.generate_data_paths(float(before_junction), float(after_junction))


@cli.command()
@click.argument('map_file', type=click.Path(exists=True))
@click.argument('before_junction', nargs=1)
@click.argument('after_junction', nargs=1)
@click.argument('parking_distance', nargs=1)
@click.argument('filter', nargs=-1)
def generate_all_paths_with_parking(map_file, before_junction, after_junction, parking_distance, filter):
    map_list = map_file.split('/')
    mmap = {
        "name": map_list[len(map_list) - 1].split('.')[0],
        "path": map_file
    }
    expm = Experiment(mmap=mmap, name="Generate All Possible Paths", plan=ParkingModel)
    if filter != () and filter[0] == "distance":
        expm.set_filter({"method": filter[0], "distance": float(filter[1]), "show_plot": filter[2]})
    if filter != () and filter[0] == "feature":
        expm.set_filter({"method": filter[0], "cells": float(filter[1]), "show_plot": filter[2]})
    expm.generate_data_paths(float(before_junction), float(after_junction), float(parking_distance))


if __name__ == "__main__":
    cli()
