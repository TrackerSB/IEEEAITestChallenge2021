from common.config import SupportedDreamViewCar, SupportedMap

scene_map: SupportedMap = SupportedMap.BorregasAve
scene_car: SupportedDreamViewCar = SupportedDreamViewCar.Lincoln2017MKZ


def _main() -> None:
    from common.apollo import ApolloModule, connect_to_dreamview
    from common.scene import generate_initial_state, load_ego, load_scene, Simulator
    from lgsvl import Vector

    sim = Simulator()
    spawn_pos = load_scene(sim, scene_map)
    initial_state = generate_initial_state(spawn_pos)
    ego = load_ego(sim, scene_car, initial_state)
    dv_connection = connect_to_dreamview(ego, Vector(0, 0, 0), "localhost", 9090, 8888)
    dv_connection.set_hd_map(scene_map.value[1])
    # dv_connection.set_vehicle(scene_car.value)
    sim.run(5)
    dv_connection.enable_module(ApolloModule.Control.value)
    sim.run(30)


if __name__ == "__main__":
    _main()
