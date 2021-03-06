from typing import Optional

from lgsvl import EgoVehicle, Sensor


def get_sensor(ego: EgoVehicle, sensor_name: str) -> Optional[Sensor]:
    from warnings import warn
    sensors = ego.get_sensors()
    for sensor in sensors:
        if sensor.name == sensor_name:
            desired_sensor = sensor
            break
    else:
        desired_sensor = None

    if desired_sensor and not desired_sensor.enabled:
        warn("Found sensor {} but it's disabled" % sensor_name)

    return desired_sensor
