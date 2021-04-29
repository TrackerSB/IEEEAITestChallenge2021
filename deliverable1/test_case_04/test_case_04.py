import unittest
import lgsvl
from decouple import config
from lgsvl.geometry import Vector
from common import SimConnection, CarControl
from common.scene import load_ego, load_npc, spawn_state
from test_case_04.encroaching import Encroaching


class TestCase04(unittest.TestCase):
    def test_finding_ego_speed_to_avoid_encroaching_npc_speed_20(self):
        def setup_cars(sim_connection: SimConnection, ego_speed: float):
            lgsvl_sim = sim_connection.connect()
            # Placing the sedan
            sedan_state = spawn_state(lgsvl_sim)
            sedan_state = CarControl.place_car_from_the_point(dimension="vertical", distance=15, state=sedan_state)
            sedan_state = CarControl.place_car_from_the_point(dimension="horizontal", distance=-8, state=sedan_state)
            sedan_state = CarControl.rotate_car_by_degree(state=sedan_state, degree=-45)
            sedan = load_npc(lgsvl_sim, "Sedan", sedan_state)

            # Placing the ego on the starting point
            ego_state = spawn_state(lgsvl_sim)
            ego_state = CarControl.drive_ego_car(ego_state, [("vertical", ego_speed)])
            ego = load_ego(lgsvl_sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)
            return {
                "sedan": sedan,
                "ego": ego,
            }

        sedan_wps = [Vector(-3.15000438690186, 0, 37.7700042724609),
                     Vector(4.85003137588501, -0.0120288729667664, 22.7699680328369)]
        encroaching = Encroaching(
            npc_speed=20,
            ego_speed=1,
            sim_connection=SimConnection(scene="CubeTown"),
            step=1,
            setup_vehicles=setup_cars,
            npc_waypoints=sedan_wps
        )
        encroaching.run()

        self.assertEqual(3.0, encroaching.ego_speed)

    @unittest.expectedFailure
    def test_EGO_encroach_NPC_speed_20_with_apollo(self):
        LGSVL__APOLLO_HOST = config("LGSVL__APOLLO_HOST")
        LGSVL__APOLLO_PORT = int(config("LGSVL__APOLLO_PORT"))
        LGSVL__DREAMVIEW_HOST = config("LGSVL__DREAMVIEW_HOST")
        MODULES = [
            'Recorder',
            'Localization',
            'Perception',
            'Transform',
            'Routing',
            'Prediction',
            'Planning',
            'Traffic Light',
            'Control'
        ]
        TARGET = Vector(4.85003185272217, -0.0120296478271484, 22.7699680328369)
        COLLISIONS = []
        SEDAN_WPS = [Vector(-3.15000438690186, 0, 37.7700042724609),
                     Vector(4.85003137588501, -0.0120288729667664, 22.7699680328369)]
        NPC_SPEED = 10

        sim_connection = SimConnection(scene="CubeTown")
        lgsvl_sim = sim_connection.connect()
        # Placing the sedan
        sedan_state = spawn_state(lgsvl_sim)
        sedan_state = CarControl.place_car_from_the_point(dimension="vertical", distance=15, state=sedan_state)
        sedan_state = CarControl.place_car_from_the_point(dimension="horizontal", distance=-8, state=sedan_state)
        sedan_state = CarControl.rotate_car_by_degree(state=sedan_state, degree=-45)
        sedan = load_npc(lgsvl_sim, "Sedan", sedan_state)

        # Placing the ego on the starting point
        ego_state = spawn_state(lgsvl_sim)
        # ego_state = CarControl.drive_ego_car(ego_state, [("vertical", 3)])
        ego = load_ego(lgsvl_sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)

        def on_collision(agent1, agent2, contact):
            COLLISIONS.append([agent1, agent2, contact])
            sim_connection.sim.close()
            print("Exception: {} collided with {}".format(agent1, agent2))

        ego.on_collision(on_collision)
        sedan.on_collision(on_collision)

        try:
            ego.connect_bridge(LGSVL__APOLLO_HOST, LGSVL__APOLLO_PORT)
            dv = lgsvl.dreamview.Connection(lgsvl_sim, ego, LGSVL__DREAMVIEW_HOST)
            dv.set_hd_map("CubeTown")
            dv.set_vehicle("Lincoln2017MKZ (Apollo 5.0)")
            dv.setup_apollo(TARGET.x, TARGET.z, MODULES)
            # Start the scenario
            waypoints = []
            for point in SEDAN_WPS:
                waypoints.append(lgsvl.DriveWaypoint(point, NPC_SPEED, sedan.state.transform.rotation))

            sedan.follow(waypoints)
            sim_connection.execute(timeout=15)
        except Exception:
            sim_connection.sim.close()
            self.fail("Failed!")

        sim_connection.sim.close()
        self.assertTrue(True, True)

