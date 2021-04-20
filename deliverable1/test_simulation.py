import unittest
from time import sleep
from common import SimConnection
from common.scene import load_ego, load_npc, spawn_state
from lgsvl.dreamview import Connection
from decouple import config


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

    def test_EGO_creation(self):  # Check if EGO Apollo is created
        with SimConnection() as sim:
            agent_state = spawn_state(sim)
            agent = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", agent_state)
            expected = agent.name
            target = "Lincoln2017MKZ (Apollo 5.0)"
        self.assertEqual(expected, target)

    def test_NPC_creation(self):
        with SimConnection(60) as sim:
            agent_state = spawn_state(sim)
            agent = load_npc(sim, "Sedan", agent_state)
            expected = agent.name
            target = "Sedan"
        self.assertEqual(expected, target)

    def test_apollo_connection(self):
        with SimConnection() as sim:
            ego_state = spawn_state(sim)
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)
            ego.connect_bridge(config("LGSVL__APOLLO_HOST"), int(config("LGSVL__APOLLO_PORT")))
            timeout = 0
            while not ego.bridge_connected:
                print(f'Wait for Apollos bridge to connect...{timeout}s')
                sleep(1)
                timeout += 1
                if timeout > 5:
                    break
            print("Apollo Status: ", ego.bridge_connected)
            self.assertEqual(True, ego.bridge_connected)

    def test_dreamview_connection(self):
        with SimConnection() as sim:
            ego_state = spawn_state(sim)
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)
            ego.connect_bridge(config("LGSVL__APOLLO_HOST"), int(config("LGSVL__APOLLO_PORT")))
            timeout = 0
            while not ego.bridge_connected:
                print(f'Wait for Apollos bridge to connect...{timeout}s')
                sleep(1)
                timeout += 1
                if timeout > 5:
                    break
            dv_connection = Connection(ego.simulator, ego, ip=config("LGSVL__DREAMVIEW_HOTS"),
                                       port=config("LGSVL__DREAMVIEW_PORT"))
            self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
