from unittest import TestCase
import lgsvl
import pytest
from lgsvl.geometry import Vector
from decouple import config
from common import SimConnection, CarControl
from common.scene import load_ego, load_npc, spawn_state


class TestCase03(TestCase):
    @pytest.mark.skip("Apollo is not running.")
    def test_ego_car_move_out_with_apollo(self):
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

        sedan1_state = spawn_state(lgsvl_sim)
        sedan1 = load_npc(lgsvl_sim, "Sedan", sedan1_state)

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
        sedan1.on_collision(on_collision)
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



