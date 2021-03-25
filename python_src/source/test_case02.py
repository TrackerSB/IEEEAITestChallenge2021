import time
import unittest
import lgsvl
from simulator import Simulator, spawn_state, create_EGO, create_NPC, cm_equal


class TestCase02(unittest.TestCase):
    def test_agent_name(self):  # Check if EGO Apollo is created
        with Simulator() as sim:
            agent = create_EGO(sim)

        self.assertEqual(agent.name, "Jaguar2015XE (Apollo 3.0)")

    def test_NPC_follow_lane(self):  # Check if NPC can follow lane
        with Simulator() as sim:
            state = spawn_state(sim)
            ego = create_EGO(sim, state)

            state = spawn_state(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            state.transform.position = state.position + 10 * forward
            truck = create_NPC(sim, "BoxTruck", state)
            truck.follow_closest_lane(True, 4)

            final_speed = ego.state.speed
            self.assertEqual(final_speed, 0.0)
            self.assertLess(truck.state.position.x, ego.state.position.x)  # truck in front of ego

    def test_vehicle_following(self):
        with Simulator() as sim:
            MAX_POV_SPEED = 11.18
            TIME_LIMIT = 25

            state = spawn_state(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            state.transform.position = state.position + 10 * forward
            truck = create_NPC(sim, "BoxTruck", state)
            truck.follow_closest_lane(True, MAX_POV_SPEED)

            state = spawn_state(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            state.velocity = 1 * forward
            ego = create_EGO(sim, state)

            def on_collision(agent1, agent2, contact):
                print("Ego collided with {}".format(agent2))

            truck.on_collision(on_collision)
            ego.on_collision(on_collision)

            control = lgsvl.VehicleControl()
            t0 = time.time()
            while True:
                sim.run(0.5)

                print(ego.state.speed, truck.state.speed)
                if ego.state.speed < MAX_POV_SPEED:
                    control.throttle += 0.1
                else:
                    control.throttle = 0
                ego.apply_control(control, True)

                if time.time() - t0 > TIME_LIMIT:
                    break