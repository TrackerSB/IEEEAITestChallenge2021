import unittest
from common import SimConnection


class TestSimulation(unittest.TestCase):
    def test_scene(self):  # Check if the right scene was loaded
        with SimConnection() as sim:
            self.assertEqual(sim.current_scene, "BorregasAve")

    def test_unload_scene(self):  # Check if a different scene gets loaded
        with SimConnection() as sim:
            self.assertEqual(sim.current_scene, "BorregasAve")
            sim.load("CubeTown")
            self.assertEqual(sim.current_scene, "CubeTown")

    def test_spawns(self):  # Check if there is at least 1 spawn point for Ego Vehicles
        with SimConnection() as sim:
            spawns = sim.get_spawn()
            self.assertGreater(len(spawns), 0)


if __name__ == '__main__':
    unittest.main()
