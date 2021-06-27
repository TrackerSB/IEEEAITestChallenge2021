def _main() -> None:
    from deliverable2.common.config import SupportedDreamViewCar, SupportedMap
    from deliverable2.common.geometry import interpolate_roads
    from deliverable2.common.open_drive_reader import get_roads_and_junctions
    from deliverable2.common.scene import generate_initial_state, get_entry_final_point, load_ego, load_scene
    from lgsvl import Simulator, dreamview
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
    initial_state = generate_initial_state(get_entry_final_point(road_points, random_connection, 0.5))
    ego = load_ego(sim, SupportedDreamViewCar.Lincoln2017MKZ, initial_state)

    # Apollo connection
    ego.connect_bridge("127.0.0.1", 9090)

    dv = dreamview.Connection(sim, ego, "127.0.0.1")
    dv.set_hd_map("")  # Need to specify the map for Apollo, otherwise, Apollo cannot drve
    dv.set_vehicle("Lincoln2017MKZ LGSVL")  # Atm, Apollo only supports Lincoln2017MKZ LGSVL
    modules = [
        'Localization',
        'Transform',
        'Routing',
        'Prediction',
        'Planning',
        'Control'
    ]
    spawns = sim.get_spawn()
    destination = spawns[0].destinations[0]
    dv.setup_apollo(destination.position.x, destination.position.z, modules)  # Apollo will drive the ego car to destination

    sim.run(10)


if __name__ == "__main__":
    _main()
