from typing import Optional

from lgsvl import EgoVehicle, Sensor


def print_sensor_states(ego: EgoVehicle) -> None:
    import logging
    sensors = ego.get_sensors()
    for sensor in sensors:
        logging.info("{} ({}): {}".format(sensor.name, type(sensor), "Enabled" if sensor.enabled else "Disabled"))


def get_sensor(ego: EgoVehicle, sensor_name: str) -> Optional[Sensor]:
    import logging
    sensors = ego.get_sensors()
    for sensor in sensors:
        if sensor.name == sensor_name:
            desired_sensor = sensor
            break
    else:
        desired_sensor = None

    if desired_sensor and not desired_sensor.enabled:
        logging.warning("Found sensor {} but it's disabled" % sensor_name)

    return desired_sensor
