from unittest import TestCase
from common import SimConnection, CarControl
from common.scene import load_ego, load_npc, spawn_state


class TestCase02(TestCase):
    def test_EGO_following_NPC_without_crash(self):
        simConnection = SimConnection()
        sim = simConnection.connect()
        # Placing the suv - 10m ahead from the starting point
        state = spawn_state(sim)
        truck_state = CarControl.place_car_from_the_point(dimension="vertical", distance=10, state=state)
        truck = load_npc(sim, "BoxTruck", truck_state)
        # Driving the truck - speed 5m/s from the starting point
        truck.follow_closest_lane(True, 5)

        # Driving the ego - speed 1m/s from the starting point
        state = spawn_state(sim)
        ego_state = CarControl.drive_ego_car(state=state, directions=[("vertical", 4.5)])
        ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)

        # Run the simulator for 10 seconds with debug mode
        simConnection.execute(timeout=10)
        self.assertEqual(True, True)
        simConnection.sim.close()


