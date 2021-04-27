import unittest
from lgsvl.utils import transform_to_forward, transform_to_right
from common import SimConnection, CarControl
from common.scene import load_ego, load_npc, spawn_state
from test_case_01.ego_control import drive_ego_no_apollo


class TestCase01(unittest.TestCase):
    def test_placing_EGO_and_NPC_on_different_lane(self):
        with SimConnection(scene="SingleLaneRoad") as sim:
            # Placing the sedan on the starting point
            state = spawn_state(sim)
            sedan = load_npc(sim, "Sedan", state)

            # Placing the ego on the left hand side of starting point - distance 3.5
            ego_state = CarControl.place_car_from_the_point(dimension="horizontal", distance=-3.5, state=state)
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)

            # sedan and ego on different line
            self.assertNotEqual(ego.state.position.z, sedan.state.position.z, "sedan and ego on different lane")

    def test_placing_EGO_and_NPC_on_same_lane(self):
        with SimConnection(scene="SingleLaneRoad") as sim:
            # Placing the sedan on the starting point
            state = spawn_state(sim)
            sedan = load_npc(sim, "Sedan", state)

            # Placing the ego on the same lane of sedan
            ego_state = CarControl.place_car_from_the_point(dimension="vertical", distance=-3.5, state=state)
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)

            # sedan and ego on same line
            self.assertEqual(ego.state.position.z, sedan.state.position.z, "sedan and ego on same lane")

    def test_placing_EGO_behind_NPC_on_same_lane(self):
        with SimConnection(scene="SingleLaneRoad") as sim:
            # Placing the sedan on the starting point
            state = spawn_state(sim)
            sedan = load_npc(sim, "Sedan", state)

            # Placing the sedan in front of the ego
            # Both vehicles are on the same lane
            ego_state = CarControl.place_car_from_the_point(dimension="vertical", distance=-3.5, state=state)
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)

            # sedan and ego on same line
            self.assertEqual(ego.state.position.z, sedan.state.position.z, "sedan and ego on same lane")
            # ego is behind sedan
            self.assertLess(sedan.state.position.x, ego.state.position.x, "ego behind sedan")

    def test_placing_EGO_between_TRUCK_and_SEDAN_on_same_lane(self):
        with SimConnection(scene="SingleLaneRoad") as sim:
            # Placing the sedan on the starting point
            state = spawn_state(sim)
            sedan = load_npc(sim, "Sedan", state)

            # Placing the ego - 5m ahead from the starting point
            state = spawn_state(sim)
            ego_state = CarControl.place_car_from_the_point(dimension="vertical", distance=5, state=state)
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)

            # Placing the suv - 10m ahead from the starting point
            state = spawn_state(sim)
            suv_state = CarControl.place_car_from_the_point(dimension="vertical", distance=10, state=state)
            suv = load_npc(sim, "SUV", suv_state)

            # sedan and ego and suv on same line
            self.assertEqual(sedan.state.position.z, ego.state.position.z, "sedan and ego on same lane")
            self.assertEqual(ego.state.position.z, suv.state.position.z, "ego and suv on same lane")
            # ego is behind suv
            self.assertLess(suv.state.position.x, ego.state.position.x, "ego behind suv")
            self.assertLess(ego.state.position.x, sedan.state.position.x, "ego in front of sedan")

    def test_placing_EGO_on_different_land_and_ego_between_SUV_and_SEDAN(self):
        with SimConnection(scene="SingleLaneRoad") as sim:
            # Placing the sedan on the starting point
            state = spawn_state(sim)
            sedan = load_npc(sim, "Sedan", state)

            # Placing the ego:
            # - 5m ahead from the starting point
            # - 3.5m on the left hand side
            state = spawn_state(sim)
            ego_state = CarControl.place_car_from_the_point(dimension="horizontal", distance=-3.5, state=state)
            ego_state = CarControl.place_car_from_the_point(dimension="vertical", distance=5, state=ego_state)
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)

            # Placing the suv - 10m ahead from the starting point
            state = spawn_state(sim)
            suv_state = CarControl.place_car_from_the_point(dimension="vertical", distance=10, state=state)
            suv = load_npc(sim, "SUV", suv_state)

            self.assertNotEqual(ego.state.position.z, sedan.state.position.z, "ego and sedan on different lane")
            self.assertNotEqual(ego.state.position.z, suv.state.position.z, "ego and suv on different lane")
            self.assertEqual(suv.state.position.z, sedan.state.position.z, "suv and sedan on same lane")
            self.assertLess(suv.state.position.x, ego.state.position.x, "ego behind suv")
            self.assertLess(ego.state.position.x, sedan.state.position.x, "ego in front of sedan")

    def test_driving_EGO_changes_lane_without_apollo(self):
        simConnection = SimConnection()
        vehicles = drive_ego_no_apollo(simConnection, npc_speed=3.9)
        sedan = vehicles["sedan"]
        suv = vehicles["suv"]
        ego = vehicles["ego"]
        # sedan and ego and suv on same line
        self.assertAlmostEqual(sedan.state.position.z, ego.state.position.z,
                               delta=1.5, msg="sedan and ego on same lane")
        self.assertAlmostEqual(suv.state.position.z, ego.state.position.z,
                               delta=1.5, msg="ego and suv on same lane")
        # ego is behind suv
        self.assertLess(suv.state.position.x, ego.state.position.x, "ego behind suv")
        self.assertLess(ego.state.position.x, sedan.state.position.x, "ego in front of sedan")
        # Close simulator
        simConnection.sim.close()

    def test_EGO_changing_lane_causes_crash_without_apollo(self):
        simConnection = SimConnection()
        collisions = drive_ego_no_apollo(simConnection, npc_speed=3.5)["collisions"]
        # Crash scenario will have non-zero collisions
        self.assertNotEqual(0, len(collisions))
        # Close simulator
        simConnection.sim.close()

    # def test_driving_EGO_changes_lane_with_apollo(self):
    #     with SimConnection(scene="SingleLaneRoad") as sim:
    #         sedan, suv, ego = drive_ego_no_apollo(sim, 3.94)
    #         # sedan and ego and suv on same line
    #         self.assertAlmostEqual(sedan.state.position.z, ego.state.position.z,
    #                                delta=1.5, msg="sedan and ego on same lane")
    #         self.assertAlmostEqual(suv.state.position.z, ego.state.position.z,
    #                                delta=1.5, msg="ego and suv on same lane")
    #         # ego is behind suv
    #         self.assertLess(suv.state.position.x, ego.state.position.x, "ego behind suv")
    #         self.assertLess(ego.state.position.x, sedan.state.position.x, "ego in front of sedan")


if __name__ == '__main__':
    unittest.main()
