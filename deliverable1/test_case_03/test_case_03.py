from unittest import TestCase
import lgsvl
import pytest
from lgsvl.geometry import Vector
from decouple import config
from common import SimConnection, CarControl
from common.scene import load_ego, load_npc, spawn_state
from test_case_03.scenario import Scenario


class TestCase03(TestCase):
    @pytest.mark.xfail
    def test_EGO_exit_park_with_incoming_NPC(self):
        NPC_START = lgsvl.geometry.Vector(120, -0.0120140314102173, -2)
        NPC_TARGET = lgsvl.geometry.Vector(60, -0.0121138095855713, -2)
        NPC_SPEED = 4
        VEHICLE_SET = [
            {"name": "Sedan", "load_vehicle": load_npc, "distance": 0, "type": "Sedan"},
            {"name": "Ego", "load_vehicle": load_ego, "distance": 10, "type": "Lincoln2017MKZ (Apollo 5.0)"},
            {"name": "SUV", "load_vehicle": load_npc, "distance": 5, "type": "SUV"},
            {"name": "Jeep", "load_vehicle": load_npc, "distance": 20, "type": "Jeep"},
        ]
        # Setup environment
        sim_connection = SimConnection()
        lgsvl_sim = sim_connection.connect()
        scenario = Scenario(sim_connection)
        # Setup vehicles position
        sedan, ego, suv, jeep = scenario.generate_vehicles(lgsvl_sim, VEHICLE_SET)
        # Setup a new NPC
        NPC_state = spawn_state(lgsvl_sim)
        NPC_state = CarControl.place_car_on_the_point(sim=lgsvl_sim, point=NPC_START, state=NPC_state)
        NPC_state = CarControl.rotate_car_by_degree(state=NPC_state, degree=-90)
        NPC = load_npc(lgsvl_sim, "Sedan", NPC_state)
        NPC.on_collision(scenario.on_collision)
        waypointsCommand = [lgsvl.DriveWaypoint(NPC_START, NPC_SPEED, NPC_state.transform.rotation),
                            lgsvl.DriveWaypoint(NPC_TARGET, NPC_SPEED, NPC_state.transform.rotation)]

        # Delay the scenario for 2s
        sim_connection.execute(timeout=2)
        try:
            NPC.follow(waypointsCommand)
            scenario.drive_ego(sim_connection, ego)
        except Exception:
            sim_connection.sim.close()
            self.fail("Failed!")

        # Passed!
        sim_connection.sim.close()
        self.assertTrue(True, True)

    def test_EGO_exit_park_lot(self):
        VEHICLE_SET = [
            {"name": "Sedan", "load_vehicle": load_npc, "distance": 0, "type": "Sedan"},
            {"name": "Ego", "load_vehicle": load_ego, "distance": 10, "type": "Lincoln2017MKZ (Apollo 5.0)"},
            {"name": "SUV", "load_vehicle": load_npc, "distance": 5, "type": "SUV"},
            {"name": "Jeep", "load_vehicle": load_npc, "distance": 20, "type": "Jeep"},
        ]
        # Setup environment
        sim_connection = SimConnection()
        lgsvl_sim = sim_connection.connect()
        scenario = Scenario(sim_connection)
        # Setup vehicles position
        sedan, ego, suv, jeep = scenario.generate_vehicles(lgsvl_sim, VEHICLE_SET)

        # Delay the scenario for 2s
        sim_connection.execute(timeout=2)
        try:
            scenario.drive_ego(sim_connection, ego)
        except Exception:
            sim_connection.sim.close()
            self.fail("Failed!")

        # Passed!
        sim_connection.sim.close()
        self.assertTrue(True, True)


    @pytest.mark.xfail
    def test_EGO_exit_park_lot_with_crash(self):
        VEHICLE_SET = [
            {"name": "Sedan", "load_vehicle": load_npc, "distance": 0, "type": "Sedan"},
            {"name": "Ego", "load_vehicle": load_ego, "distance": 5, "type": "Lincoln2017MKZ (Apollo 5.0)"},
            {"name": "SUV", "load_vehicle": load_npc, "distance": 12, "type": "SUV"},
            {"name": "Jeep", "load_vehicle": load_npc, "distance": 17, "type": "Jeep"},
        ]
        # Setup environment
        sim_connection = SimConnection()
        lgsvl_sim = sim_connection.connect()
        scenario = Scenario(sim_connection)
        # Setup vehicles position
        sedan, ego, suv, jeep = scenario.generate_vehicles(lgsvl_sim, VEHICLE_SET)

        # Delay the scenario for 2s
        sim_connection.execute(timeout=2)
        try:
            scenario.drive_ego(sim_connection, ego)
        except Exception:
            sim_connection.sim.close()
            self.fail("Failed!")

        # Passed!
        sim_connection.sim.close()
        self.assertTrue(True, True)


    @pytest.mark.skip("Apollo is not running.")
    def test_EGO_exit_with_apollo(self):
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
        EGO_TARGET = Vector(114.219772338867, -0.003660649061203, -1.39988207817078)
        COLLISIONS = []

        # Setup environment
        sim_connection = SimConnection()
        lgsvl_sim = sim_connection.connect()

        NPC_state = spawn_state(lgsvl_sim)
        NPC = load_npc(lgsvl_sim, "Sedan", NPC_state)

        sedan2_state = spawn_state(lgsvl_sim)
        sedan2_state = CarControl.place_car_from_the_point(dimension="vertical", distance=10, state=sedan2_state)
        sedan2 = load_npc(lgsvl_sim, "Sedan", sedan2_state)
        sedan3_state = spawn_state(lgsvl_sim)
        sedan3_state = CarControl.place_car_from_the_point(dimension="vertical", distance=15, state=sedan3_state)
        sedan3 = load_npc(lgsvl_sim, "Sedan", sedan3_state)

        # Placing the ego on the starting point
        ego_state = spawn_state(lgsvl_sim)
        ego_state = CarControl.place_car_from_the_point(dimension="vertical", distance=5, state=ego_state)
        ego = load_ego(lgsvl_sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)

        sim_connection.execute(timeout=5, debug=True, vehicles=[ego])

        def on_collision(agent1, agent2, contact):
            COLLISIONS.append([agent1, agent2, contact])
            sim_connection.sim.close()
            # print("Exception: {} collided with {}".format(agent1, agent2))
            raise Exception()

        ego.on_collision(on_collision)
        NPC.on_collision(on_collision)
        sedan2.on_collision(on_collision)
        sedan3.on_collision(on_collision)

        try:
            ego.connect_bridge(LGSVL__APOLLO_HOST, LGSVL__APOLLO_PORT)
            dv = lgsvl.dreamview.Connection(lgsvl_sim, ego, LGSVL__DREAMVIEW_HOST)
            dv.set_hd_map("CubeTown")
            dv.set_vehicle("Lincoln2017MKZ (Apollo 5.0)")
            dv.setup_apollo(EGO_TARGET.x, EGO_TARGET.z, MODULES)
            # Start the scenario
            sim_connection.execute(timeout=15)
        except Exception:
            sim_connection.sim.close()
            self.fail("Failed!")

        sim_connection.sim.close()
        self.assertTrue(True, True)



