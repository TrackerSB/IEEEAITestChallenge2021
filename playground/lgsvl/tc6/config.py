from dataclasses import dataclass
from typing import Optional

from tc6.locations import Location


@dataclass
class TestConfig:
    ego_car_model: str
    ego_car_name: str
    ego_speed: float  # in km/h
    ego_distance: Optional[float]  # in m: None --> Calculate a distance which enforces a crash with the pedestrian
    pedestrian_direction: bool  # Iff True (False) pedestrian moves from A to B (B to A)
    test_place: Location
