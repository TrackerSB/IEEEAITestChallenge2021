from unittest import TestCase

from lgsvl import Transform, Vector

from common import SimConnection
from common.scene import load_npc, load_ego, generate_initial_state


class TestCase02(TestCase):
    def test_basicSetup(self):
        with SimConnection(scene="Shalun") as sim:
            initial_bus_position = Vector(42, 0, 4)
            initial_bus_rotation = Vector(0, 250, 0)
            initial_bus_state = generate_initial_state(Transform(initial_bus_position, initial_bus_rotation), None)
            school_bus = load_npc(sim, "SchoolBus", initial_bus_state)

            initial_ego_position = Vector(22, 0, -8)
            initial_ego_rotation = Vector(0, 70, 0)
            initial_ego_state = generate_initial_state(Transform(initial_ego_position, initial_ego_rotation), 10)
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", initial_ego_state)
            sim.run()

            self.skipTest("Test not implemented yet")
