from typing import List, Dict

from lgsvl import Simulator
from opendrive2lanelet.opendriveparser.elements.junction import Connection as ODConnection
from shapely.geometry import Point


def _execute_test(sim: Simulator, road_points: Dict[int, List[Point]], connection: ODConnection) -> None:
    from common.apollo import connect_to_dreamview
    from common.config import SupportedDreamViewCar, SupportedMap, ApolloModule
    from common.scene import generate_initial_state, get_entry_final_point, load_ego, load_scene
    load_scene(sim, SupportedMap.BorregasAve)
    entry_estimation, final_estimation = get_entry_final_point(road_points, connection)
    initial_state = generate_initial_state(entry_estimation)
    ego = load_ego(sim, SupportedDreamViewCar.Lincoln2017MKZ, initial_state)

    # Connect DreamView
    dreamview = connect_to_dreamview(ego, final_estimation.position, "127.0.0.1", 9090, 8888)
    dreamview.set_hd_map("Borregas Ave")
    dreamview.enable_module(ApolloModule.Control.value)

    sim.run(10)


def _main() -> None:
    from common.geometry import interpolate_roads
    from common.open_drive_reader import get_roads_and_junctions

    # Parse map roads and junctions
    roads, junctions = get_roads_and_junctions("borregasave.xodr")
    road_points, _ = interpolate_roads(roads)

    # Setup simulation
    sim = Simulator()

    # Find random position on any junction
    for junction in junctions:
        for connection in junction.connections:
            _execute_test(sim, road_points, connection)


if __name__ == "__main__":
    _main()
