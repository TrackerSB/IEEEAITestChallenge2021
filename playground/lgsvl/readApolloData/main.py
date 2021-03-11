import asyncio
from time import sleep

from lgsvl import EgoVehicle


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
    from common.scene import load_scene, generate_initial_state, load_ego, add_random_traffic
    from common.sensor import get_sensor
    from common.simulator import connect_simulation
    from loadBasicScenario.main import _print_sensor_state
    from lgsvl.sensor import LidarSensor, RadarSensor

    sim = connect_simulation("localhost", 8181)
    spawn_pos = load_scene(sim, "Shalun")
    initial_state = generate_initial_state(spawn_pos)
    ego = load_ego(sim, "Jaguar2015XE (Apollo 5.0, many sensors)", initial_state)
    _connect_to_bridge(ego, "127.0.0.1", 9090)
    add_random_traffic(sim)
    sensors = ego.get_sensors()
    _print_sensor_state(sensors)
    lidar_sensor: LidarSensor = get_sensor(ego, "Lidar")
    radar_sensor: RadarSensor = get_sensor(ego, "Radar")

    def dump(obj):
        for attr in dir(obj):
            if hasattr(obj, attr):
                print("obj.%s = %s" % (attr, getattr(obj, attr)))

    for i in range(5):
        sim.run(2)
        dump(lidar_sensor)
        dump(radar_sensor)

    sim.stop()


if __name__ == "__main__":
    _main()
