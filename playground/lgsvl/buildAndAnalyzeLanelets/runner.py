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
def generate_all_paths(map_file, before_junction, after_junction):
    map_list = map_file.split('/')
    mmap = {
        "name": map_list[len(map_list) - 1].split('.')[0],
        "path": map_file
    }
    expm = Experiment(mmap=mmap, name="Generate All Possible Paths", plan=StraightModel)
    expm.generate_data_paths(float(before_junction), float(after_junction))


@cli.command()
@click.argument('map_file', type=click.Path(exists=True))
@click.argument('before_junction', nargs=1)
@click.argument('after_junction', nargs=1)
@click.argument('parking_distance', nargs=1)
def generate_all_paths_with_parking(map_file, before_junction, after_junction, parking_distance):
    map_list = map_file.split('/')
    mmap = {
        "name": map_list[len(map_list) - 1].split('.')[0],
        "path": map_file
    }
    expm = Experiment(mmap=mmap, name="Generate All Possible Paths", plan=ParkingModel)
    expm.generate_data_paths(float(before_junction), float(after_junction), float(parking_distance))


if __name__ == "__main__":
    cli()
