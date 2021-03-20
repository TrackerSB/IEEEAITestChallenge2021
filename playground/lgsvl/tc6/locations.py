from collections import namedtuple

from lgsvl import Vector

Location = namedtuple("Location", "map_name ped_pos_a ped_crash_pos ped_pos_b")

LOC_1_VARA = Location("San Francisco", Vector(-185, 10.25, 139), Vector(-202, 10.25, 139), Vector(-205, 10.25, 139))
LOC_1_VARB = Location("San Francisco", Vector(-205, 10.25, 139), Vector(-190, 10.25, 139), Vector(-185, 10.25, 139))
