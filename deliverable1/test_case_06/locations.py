from dataclasses import dataclass
from typing import Optional, List

from lgsvl import Vector


@dataclass
class Location:
    map_name: str
    ped_pos_a: Vector
    ped_crash_pos: Vector
    ped_pos_b: Vector
    max_ego_distance: float  # Ensure AVs are not placed outside the map
    # The following can be used to enforce an approach direction (e.g. in case of non orthogonal cross walks)
    ego_approach_rotation: Optional[float] = None  # In degree


LOC_1_VARA = Location("SanFrancisco", Vector(-185, 10.25, 139), Vector(-202, 10.25, 139),
                      Vector(-205, 10.25, 139), 500)
LOC_1_VARB = Location("SanFrancisco", Vector(-205, 10.25, 139), Vector(-190, 10.25, 139),
                      Vector(-185, 10.25, 139), 500)

LOC_2_VARA = Location("SanFrancisco", Vector(-185, 10.25, 585), Vector(-202, 10.25, 587),
                      Vector(-204, 10.25, 587), 500, 180)
LOC_2_VARB = Location("SanFrancisco", Vector(-204, 10.25, 587), Vector(-189.5, 10.25, 586),
                      Vector(-185, 10.25, 585), 500, 0)

LOC_3_VARA = Location("CubeTown", Vector(-7, 0, 42), Vector(3, 0, 42), Vector(7, 0, 42), 80)

LOC_4_VARA = Location("CubeTown", Vector(7, 0, -42), Vector(-3, 0, -42), Vector(-7, 0, -42), 80)

ALL_LOCATIONS: List = [
    LOC_1_VARA, LOC_1_VARB,
    LOC_2_VARA, LOC_2_VARB,
    LOC_3_VARA,
    LOC_4_VARA
]
