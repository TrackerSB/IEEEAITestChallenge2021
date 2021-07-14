import lgsvl
import time
from environs import Env
from ..scenario import Scenario
from .common import spawn_state, place_car_on_the_point

env = Env()

LGSVL__SIMULATOR_HOST = env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1")
LGSVL__SIMULATOR_PORT = env.int("LGSVL__SIMULATOR_PORT", 8181)
LGSVL__AUTOPILOT_0_HOST = env.str("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
LGSVL__AUTOPILOT_0_PORT = env.int("LGSVL__AUTOPILOT_0_PORT", 9090)
TIME_LIMIT = 60  # seconds
MAPS = {
    "BorregasAve": "Borregas Ave",
    "CubeTown": "Cubetown",
    "AutonomouStuff": "Autonomous Stuff",
    "SanFrancisco": "San Francisco",
    "Shalun": "Shalun",
    "Gomentum": "Gomentum"
}

# Wait until an ego vehicle approaches this controllable object within 50 meters
# Change current state to green and wait for 60s, red & yellow - 0s
# Loop over this control policy from the beginning
TRAFFIC_LIGHT_POLICY = "trigger=50;green=60;yellow=0;red=0;loop"


class StraightModel:
    @staticmethod
    def run(scenario: Scenario, time_limit: int = TIME_LIMIT):
        print("Map {}: {} - ".format(scenario.map, scenario.ID), end="")
        sim = lgsvl.Simulator(LGSVL__SIMULATOR_HOST, LGSVL__SIMULATOR_PORT)

        sim.load(scenario.map)
        # Get a list of controllable objects
        controllables = sim.get_controllables("signal")
        for c in controllables:
            signal = sim.get_controllable(c.transform.position, "signal")
            signal.control(TRAFFIC_LIGHT_POLICY)

        START_POINT = lgsvl.geometry.Vector(scenario.start[0], 0, scenario.start[1])
        ego_state = spawn_state(sim)
        ego_state = place_car_on_the_point(sim=sim, point=START_POINT, state=ego_state)

        ego = sim.add_agent("2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921", lgsvl.AgentType.EGO, ego_state)
        ego.connect_bridge(LGSVL__AUTOPILOT_0_HOST, LGSVL__AUTOPILOT_0_PORT)

        dv = lgsvl.dreamview.Connection(sim, ego, LGSVL__AUTOPILOT_0_HOST)
        dv.set_hd_map(scenario.map.value[1])
        dv.set_vehicle('Lincoln2017MKZ LGSVL')

        modules = [
            'Localization',
            'Transform',
            'Routing',
            'Prediction',
            'Planning',
            'Control'
        ]
        dv.setup_apollo(scenario.end[0], scenario.end[1], modules)
        destination = lgsvl.geometry.Vector(scenario.end[0], 0, scenario.end[1])

        # Run a simulation
        is_test_failed = False
        try:
            t0 = time.time()
            while True:
                sim.run(0.5)
                currentPos = ego.state.position
                # print(lgsvl.evaluator.separation(currentPos, destination))
                if lgsvl.evaluator.separation(currentPos, destination) < 10:
                    raise lgsvl.evaluator.TestException(
                        "PASSED: EGO does reach to destination, distance {} < 10!".format(lgsvl.evaluator.separation(currentPos, destination))
                    )
                else:
                    if time.time() - t0 > time_limit:
                        is_test_failed = True
                        raise lgsvl.evaluator.TestException(
                            "FAILED: Timeout! EGO does reach to destination, distance {} > 10!".format(lgsvl.evaluator.separation(currentPos, destination))
                        )
        except lgsvl.evaluator.TestException as e:
            print("{}".format(e))

        # Close simulator
        dv.disable_apollo()
        sim.close()

        # Send a message
        if is_test_failed:
            raise Exception("TESTING FAILED!")