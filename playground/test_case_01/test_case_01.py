import unittest
from lgsvl import VehicleControl
from lgsvl.utils import transform_to_forward, transform_to_right
from common import SimConnection
from common.scene import load_ego, load_npc, spawn_state


class TestCase01(unittest.TestCase):
    def test_EGO_and_NPC_on_different_lane(self):
        with SimConnection(scene="SingleLaneRoad") as sim:
            state = spawn_state(sim)
            sedan = load_npc(sim, "Sedan", state)
            sedan.follow_closest_lane(True, 4)

            right = transform_to_right(state.transform)
            state.transform.position = state.position - 3.5 * right
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", state)

            # sedan and ego on different line
            self.assertNotEqual(ego.state.position.z, sedan.state.position.z, "sedan and ego on different lane")

    def test_EGO_and_NPC_on_same_lane(self):
        with SimConnection(scene="SingleLaneRoad") as sim:
            state = spawn_state(sim)
            sedan = load_npc(sim, "Sedan", state)
            sedan.follow_closest_lane(True, 4)

            forward = transform_to_forward(state.transform)
            state.transform.position = state.position - 3.5 * forward
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", state)

            # sedan and ego on same line
            self.assertEqual(ego.state.position.z, sedan.state.position.z, "sedan and ego on same lane")

    def test_EGO_behind_NPC_on_same_lane(self):
        with SimConnection(scene="SingleLaneRoad") as sim:
            state = spawn_state(sim)
            sedan = load_npc(sim, "Sedan", state)
            sedan.follow_closest_lane(True, 4)

            forward = transform_to_forward(state.transform)
            state.transform.position = state.position - 3.5 * forward
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", state)

            # sedan and ego on same line
            self.assertEqual(ego.state.position.z, sedan.state.position.z, "sedan and ego on same lane")
            # ego is behind sedan
            self.assertLess(sedan.state.position.x, ego.state.position.x, "ego behind sedan")

    def test_EGO_between_TRUCK_and_SEDAN_on_same_lane(self):
        with SimConnection(scene="SingleLaneRoad") as sim:
            state = spawn_state(sim)
            sedan = load_npc(sim, "Sedan", state)

            state = spawn_state(sim)
            forward = transform_to_forward(state.transform)
            state.transform.position = state.position + 5 * forward
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", state)

            state = spawn_state(sim)
            forward = transform_to_forward(state.transform)
            state.transform.position = state.position + 10 * forward
            suv = load_npc(sim, "SUV", state)

            # sedan and ego and suv on same line
            self.assertEqual(sedan.state.position.z, ego.state.position.z, "sedan and ego on same lane")
            self.assertEqual(ego.state.position.z, suv.state.position.z, "ego and suv on same lane")
            # ego is behind suv
            self.assertLess(suv.state.position.x, ego.state.position.x, "ego behind suv")
            self.assertLess(ego.state.position.x, sedan.state.position.x, "ego in front of sedan")

    def test_EGO_on_different_land_and_ego_between_SUV_and_SEDAN(self):
        with SimConnection(scene="SingleLaneRoad") as sim:
            state = spawn_state(sim)
            sedan = load_npc(sim, "Sedan", state)

            state = spawn_state(sim)
            right = transform_to_right(state.transform)
            state.transform.position = state.position - 3.5 * right
            forward = transform_to_forward(state.transform)
            state.transform.position = state.position + 5 * forward
            ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", state)

            state = spawn_state(sim)
            forward = transform_to_forward(state.transform)
            state.transform.position = state.position + 10 * forward
            suv = load_npc(sim, "SUV", state)

            self.assertNotEqual(ego.state.position.z, sedan.state.position.z, "ego and sedan on different lane")
            self.assertNotEqual(ego.state.position.z, suv.state.position.z, "ego and suv on different lane")
            self.assertEqual(suv.state.position.z, sedan.state.position.z, "suv and sedan on same lane")
            self.assertLess(suv.state.position.x, ego.state.position.x, "ego behind suv")
            self.assertLess(ego.state.position.x, sedan.state.position.x, "ego in front of sedan")

    def test_EGO_changes_lane(self):
        with SimConnection(scene="SingleLaneRoad") as sim:
            npc_speed = 3.94
            is_collided = True

            while is_collided:
                sim.reset()
                collisions = []
                state = spawn_state(sim)
                sedan = load_npc(sim, "Sedan", state)
                sedan.follow_closest_lane(True, npc_speed)

                state = spawn_state(sim)
                forward = transform_to_forward(state.transform)
                state.transform.position = state.position + 15 * forward
                suv = load_npc(sim, "SUV", state)
                suv.follow_closest_lane(True, npc_speed)

                state = spawn_state(sim)
                forward = transform_to_forward(state.transform)
                right = transform_to_right(state.transform)
                state.transform.position = state.position - 3.5 * right
                state.velocity = 5 * forward
                ego = load_ego(sim, "Lincoln2017MKZ (Apollo 5.0)", state)

                def on_collision(agent1, agent2, contact):
                    collisions.append([agent1, agent2, contact])
                    print(npc_speed)
                    print("{} collided with {}".format(agent1, agent2))

                sedan.on_collision(on_collision)
                suv.on_collision(on_collision)
                ego.on_collision(on_collision)

                sim.run(5, 2)
                control = VehicleControl()
                control.steering = 0.037
                ego.apply_control(control, True)
                sim.run(5, 2)
                control.steering = -0.041
                ego.apply_control(control, True)
                sim.run(5, 2)
                control.steering = 0
                ego.apply_control(control, True)
                sim.run(7, 2)
                control.braking = 1
                ego.apply_control(control, True)
                sim.run(3, 2)

                if suv.state.position.x < ego.state.position.x < sedan.state.position.x and len(collisions) == 0:
                    is_collided = False
                    print(npc_speed)
                else:
                    is_collided = True
                    npc_speed += 0.01

            # sedan and ego and suv on same line
            self.assertAlmostEqual(sedan.state.position.z, ego.state.position.z,
                                   delta=1.5, msg="sedan and ego on same lane")
            self.assertAlmostEqual(suv.state.position.z, ego.state.position.z,
                                   delta=1.5, msg="ego and suv on same lane")
            # ego is behind suv
            self.assertLess(suv.state.position.x, ego.state.position.x, "ego behind suv")
            self.assertLess(ego.state.position.x, sedan.state.position.x, "ego in front of sedan")


if __name__ == '__main__':
    unittest.main()
