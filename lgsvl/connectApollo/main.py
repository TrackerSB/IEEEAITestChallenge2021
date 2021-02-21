from lgsvl import EgoVehicle

from common.scene import load_scene, load_ego, generate_initial_state, add_random_traffic
from common.simulator import connect_simulation


def _connect_to_bridge(ego: EgoVehicle, host: str, port: int, timeout_secs: int = 5) -> None:
    from lgsvl.simulator import env
    from time import sleep
    ego.connect_bridge(env.str("LGSVL__AUTOPILOT_0_HOST", host),
                       env.int("LGSVL__AUTOPILOT_0_PORT", port))
    seconds_waited = 0
    while not ego.bridge_connected:
        sleep(1)
        seconds_waited += 1
        if seconds_waited > timeout_secs:
            raise ConnectionRefusedError("Connecting to bridge timed out")


def _main() -> None:
    sim = connect_simulation("localhost", 8181)
    spawn_pos = load_scene(sim, "Shalun")
    initial_state = generate_initial_state(spawn_pos)
    ego = load_ego(sim, "Jaguar2015XE (Apollo 5.0, many sensors)", initial_state)
    _connect_to_bridge(ego, "127.0.0.1", 9090)
    add_random_traffic(sim)
    sim.run()


if __name__ == "__main__":
    _main()
