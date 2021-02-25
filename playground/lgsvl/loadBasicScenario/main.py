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
    from common.scene import add_random_traffic, generate_initial_state, load_ego, load_scene
    from common.simulator import connect_simulation
    sim = connect_simulation("127.0.0.1", 8181)
    spawn_pos = load_scene(sim, "Shalun")

    initial_state = generate_initial_state(spawn_pos, 20)
    ego = load_ego(sim, "Jaguar2015XE (Apollo 5.0, radar)", initial_state)
    # _detect_collisions(ego)  # FIXME Collisions seem not to be detected
    ego.apply_control(_generate_control_command(), True)

    sensors = ego.get_sensors()
    _print_sensor_state(sensors)

    add_random_traffic(sim)
    sim.run()


if __name__ == "__main__":
    _main()
