def _main() -> None:
    from common.config import SupportedDreamViewCar, SupportedMap
    from common.geometry import interpolate_roads
    from common.open_drive_reader import get_roads_and_junctions
    from common.scene import generate_initial_state, get_entry_point, load_ego, load_scene
    from lgsvl import Simulator
    from random import randint

    # Parse map roads and junctions
    roads, junctions = get_roads_and_junctions("borregasave.xodr")
    road_points, _ = interpolate_roads(roads)

    # Find random position on any junction
    random_junction = junctions[randint(0, len(junctions))]
    random_connection = random_junction.connections[randint(0, len(random_junction.connections))]

    # Setup simulation
    sim = Simulator()
    load_scene(sim, SupportedMap.BorregasAve)
    initial_state = generate_initial_state(get_entry_point(road_points, random_connection))
    ego = load_ego(sim, SupportedDreamViewCar.Jaguar2015XE, initial_state)

    sim.run(10)


if __name__ == "__main__":
    _main()
