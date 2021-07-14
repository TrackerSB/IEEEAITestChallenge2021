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
def generate_all_paths(map_file):
    map_list = map_file.split('/')
    mmap = {
        "name": map_list[len(map_list)-1].split('.')[0],
        "path": map_file
    }
    expm = Experiment(mmap=mmap, name="Generate All Possible Paths", plan=StraightModel)
    expm.generate_data_paths()


if __name__ == "__main__":
    cli()
