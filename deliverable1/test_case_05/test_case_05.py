import unittest
import lgsvl
from decouple import config
from lgsvl.geometry import Vector
from common import SimConnection, CarControl
from common.scene import load_ego, load_npc, spawn_state
from test_case_05.encroaching import Encroaching
from test_case_05.school_bus import SchoolBus


class TestCase05(unittest.TestCase):
    def test_EGO_respond_SCHOOLBUS_without_crash(self):
        sim_connection = SimConnection(scene="CubeTown")
        scenario = SchoolBus(
            sim_connection=sim_connection,
            ego_target=Vector(3.03013730049133, -0.00637590885162354, -16.5673313140869),
            ego_speed=6,
            ego_brake=0.2,
            npc_speed=6,
            npc_source=Vector(-3.84999561309814, -0.00320455431938171, 10.877103805542),
            npc_target=Vector(3.03013730049133, -0.00320455431938171, -5.877103805542),
        )
        try:
            scenario.run()
        except Exception:
            sim_connection.sim.close()
            self.fail("Failed!")

        # Passed!
        sim_connection.sim.close()
        self.assertTrue(True, True)

    @unittest.expectedFailure
    def test_EGO_respond_SCHOOLBUS_with_crash(self):
        sim_connection = SimConnection(scene="CubeTown")
        scenario = SchoolBus(
            sim_connection=sim_connection,
            ego_target=Vector(3.03013730049133, -0.00637590885162354, -16.5673313140869),
            ego_speed=7,
            ego_brake=0,
            npc_speed=6,
            npc_source=Vector(-3.84999561309814, -0.00320455431938171, 10.877103805542),
            npc_target=Vector(3.03013730049133, -0.00320455431938171, -5.877103805542),
        )
        try:
            scenario.run()
        except Exception:
            sim_connection.sim.close()
            self.fail("Failed!")

        # Passed!
        sim_connection.sim.close()
        self.assertTrue(True, True)

    def test_finding_ego_speed_to_avoid_encroaching_schoolbus_speed_6(self):
        def setup_cars(sim_connection: SimConnection, ego_speed: float, npc_speed: float):
            lgsvl_sim = sim_connection.connect()
            # Placing the school_bus
            school_bus_state = spawn_state(lgsvl_sim)
            school_bus = load_npc(lgsvl_sim, "SchoolBus", school_bus_state)

            # Placing the ego on the starting point
            ego_state = spawn_state(lgsvl_sim)
            ego_state = CarControl.place_car_from_the_point(dimension="horizontal", distance=-6, state=ego_state)
            ego_state = CarControl.drive_ego_car(ego_state, [("vertical", ego_speed)])
            ego = load_ego(lgsvl_sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)
            return {
                "school_bus": school_bus,
                "ego": ego,
            }

        school_bus_wps = [Vector(-3.31942486763, -0.0809718370437622, 24.2049713134766),
                          Vector(-3.84999561309814, -0.00320455431938171, 14.877103805542),
                          Vector(3.84999561309814, -0.00320455431938171, -20.877103805542)]
        npc_speed = 6
        ego_speed = 6
        encroaching = Encroaching(
            npc_speed=npc_speed,
            ego_speed=ego_speed,
            sim_connection=SimConnection(scene="CubeTown"),
            step=1,
            setup_vehicles=setup_cars,
            npc_waypoints=school_bus_wps
        )
        encroaching.run()

        self.assertEqual(8.0, encroaching.ego_speed)

    @unittest.expectedFailure
    def test_EGO_encroach_schoolbus_speed_6_with_apollo(self):
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
        TARGET = Vector(3.03013730049133, -0.00637590885162354, -16.5673313140869)
        COLLISIONS = []
        SEDAN_WPS = [Vector(-3.31942486763, -0.0809718370437622, 24.2049713134766),
                     Vector(-3.84999561309814, -0.00320455431938171, 14.877103805542),
                     Vector(3.84999561309814, -0.00320455431938171, -20.877103805542)]
        NPC_SPEED = 6

        sim_connection = SimConnection(scene="CubeTown")
        lgsvl_sim = sim_connection.connect()
        # Placing the school_bus
        school_bus_state = spawn_state(lgsvl_sim)
        school_bus = load_npc(lgsvl_sim, "SchoolBus", school_bus_state)

        # Placing the ego on the starting point
        ego_state = spawn_state(lgsvl_sim)
        ego_state = CarControl.place_car_from_the_point(dimension="horizontal", distance=-6, state=ego_state)
        # ego_state = CarControl.drive_ego_car(ego_state, [("vertical", 6)])
        ego = load_ego(lgsvl_sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)

        def on_collision(agent1, agent2, contact):
            COLLISIONS.append([agent1, agent2, contact])
            sim_connection.sim.close()
            print("Exception: {} collided with {}".format(agent1, agent2))

        ego.on_collision(on_collision)
        school_bus.on_collision(on_collision)

        try:
            ego.connect_bridge(LGSVL__APOLLO_HOST, LGSVL__APOLLO_PORT)
            dv = lgsvl.dreamview.Connection(lgsvl_sim, ego, LGSVL__DREAMVIEW_HOST)
            dv.set_hd_map("CubeTown")
            dv.set_vehicle("Lincoln2017MKZ (Apollo 5.0)")
            dv.setup_apollo(TARGET.x, TARGET.z, MODULES)
            # Start the scenario
            school_bus.follow_closest_lane(follow=True, max_speed=10)
            waypoints = []
            for point in SEDAN_WPS:
                waypoints.append(lgsvl.DriveWaypoint(point, NPC_SPEED, school_bus.state.transform.rotation))

            school_bus.follow(waypoints)
            sim_connection.execute(timeout=15)
        except Exception:
            sim_connection.sim.close()
            self.fail("Failed!")

        sim_connection.sim.close()
        self.assertTrue(True, True)

