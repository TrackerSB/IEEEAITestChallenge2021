import unittest
import lgsvl
from simulator import Simulator, spawn_state, create_EGO, create_NPC, cm_equal


class TestCase01(unittest.TestCase):
    def test_agent_name(self):  # Check if EGO Apollo is created
        with Simulator() as sim:
            agent = create_EGO(sim)

        self.assertEqual(agent.name, "Jaguar2015XE (Apollo 3.0)")

    def test_different_spawns(self):  # Check if EGO is spawned in the spawn positions
        with Simulator() as sim:
            spawns = sim.get_spawn()
            agent = create_EGO(sim)
            cm_equal(self, agent.state.position, spawns[0].position, "Spawn Position 0")
            cm_equal(self, agent.state.rotation, spawns[0].rotation, "Spawn Rotation 0")

    def test_agent_velocity(self):  # Check EGO velocity
        with Simulator(60) as sim:
            state = spawn_state(sim)
            agent = create_EGO(sim)
            cm_equal(self, agent.state.velocity, state.velocity, "0 Velocity")

            sim.reset()
            forward = lgsvl.utils.transform_to_right(state.transform)
            state.velocity = 5 * forward
            agent = sim.add_agent("Jaguar2015XE (Apollo 3.0)", lgsvl.AgentType.EGO, state)

            cm_equal(self, agent.state.velocity, state.velocity, "5 Velocity")

    def test_ego_steering(self):  # Check that a steering command can be given to an EGO vehicle, and the car turns
        with Simulator() as sim:
            state = spawn_state(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            right = lgsvl.utils.transform_to_right(state.transform)
            state.transform.position = state.position - 3.5 * right
            state.velocity = 5 * forward
            ego = create_EGO(sim, state)
            initial_rotation = ego.state.rotation

            sim.run(5)
            control = lgsvl.VehicleControl()
            control.steering = 0.037
            ego.apply_control(control, True)
            sim.run(5)
            control.steering = -0.041
            ego.apply_control(control, True)
            sim.run(5)
            control.steering = 0
            ego.apply_control(control, True)
            sim.run(7)
            control.braking = 1
            ego.apply_control(control, True)
            sim.run(3)
            final_rotation = ego.state.rotation
            final_speed = ego.state.speed

            self.assertNotAlmostEqual(initial_rotation.y, final_rotation.y)
            self.assertNotAlmostEqual(final_speed, 0)

    def test_NPC_follow_lane(self):  # Check if NPC can follow lane
        with Simulator() as sim:
            state = spawn_state(sim)
            sedan = create_NPC(sim, "Sedan", state)
            sedan.follow_closest_lane(True, 4)

            state = spawn_state(sim)
            forward = lgsvl.utils.transform_to_forward(state.transform)
            state.transform.position = state.position + 15 * forward
            truck = create_NPC(sim, "BoxTruck", state)
            truck.follow_closest_lane(True, 4)

            state = spawn_state(sim)
            right = lgsvl.utils.transform_to_right(state.transform)
            state.transform.position = state.position - 3.5 * right
            ego = create_EGO(sim, state)
            final_speed = ego.state.speed
            self.assertEqual(final_speed, 0.0)

            self.assertEqual(ego.state.position.x, sedan.state.position.x)  # sedan and ego on same line
            self.assertLess(truck.state.position.x, ego.state.position.x)  # truck in front of ego
            self.assertLess(truck.state.position.x, sedan.state.position.x)  # truck in front of sedan

    def test_merge_lane(self):
        with Simulator() as sim:
            npc_speed = 3.87
            is_collided = True

            while is_collided:
                sim.reset()
                collisions = []
                state = spawn_state(sim)
                sedan = create_NPC(sim, "Sedan", state)
                sedan.follow_closest_lane(True, npc_speed)

                state = spawn_state(sim)
                forward = lgsvl.utils.transform_to_forward(state.transform)
                state.transform.position = state.position + 15 * forward
                truck = create_NPC(sim, "BoxTruck", state)
                truck.follow_closest_lane(True, npc_speed)

                state = spawn_state(sim)
                forward = lgsvl.utils.transform_to_forward(state.transform)
                right = lgsvl.utils.transform_to_right(state.transform)
                state.transform.position = state.position - 3.5 * right
                state.velocity = 5 * forward
                ego = create_EGO(sim, state)

                def on_collision(agent1, agent2, contact):
                    collisions.append([agent1, agent2, contact])
                    print(npc_speed)
                    print("{} collided with {}".format(agent1, agent2))

                sedan.on_collision(on_collision)
                truck.on_collision(on_collision)
                ego.on_collision(on_collision)

                sim.run(5)
                control = lgsvl.VehicleControl()
                control.steering = 0.037
                ego.apply_control(control, True)
                sim.run(5)
                control.steering = -0.041
                ego.apply_control(control, True)
                sim.run(5)
                control.steering = 0
                ego.apply_control(control, True)
                sim.run(7)
                control.braking = 1
                ego.apply_control(control, True)
                sim.run(3)

                if truck.state.position.x < ego.state.position.x < sedan.state.position.x and len(collisions) == 0:
                    is_collided = False
                    print(npc_speed)
                else:
                    is_collided = True
                    npc_speed += 0.01
