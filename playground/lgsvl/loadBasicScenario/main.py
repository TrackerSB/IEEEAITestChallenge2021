from lgsvl.agent import VehicleControl


def _print_sensor_state(sensors):
    for sensor in sensors:
        print("{} ({}): {}".format(sensor.name, type(sensor), "Enabled" if sensor.enabled else "Disabled"))


def _generate_control_command() -> VehicleControl:
    control = VehicleControl()
    control.throttle = 0.1
    control.steering = 0.05
    return control


def _main() -> None:
    from common.apollo import SupportedDreamViewCar
    from common.scene import add_random_traffic, generate_initial_state, load_ego, load_scene, SupportedMap
    from lgsvl import Simulator

    sim = Simulator()
    spawn_pos = load_scene(sim, SupportedMap.Shalun)
    initial_state = generate_initial_state(spawn_pos, 20)
    ego = load_ego(sim, SupportedDreamViewCar.Jaguar2015XE.value, initial_state)
    # _detect_collisions(ego)  # FIXME Collisions seem not to be detected
    ego.apply_control(_generate_control_command(), True)

    sensors = ego.get_sensors()
    _print_sensor_state(sensors)

    add_random_traffic(sim)

    sim.run(10)


if __name__ == "__main__":
    _main()
