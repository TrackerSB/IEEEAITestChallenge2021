from environs import Env
from .map import MapModel
import lgsvl
import time

env = Env()

LGSVL__SIMULATOR_HOST = env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1")
LGSVL__SIMULATOR_PORT = env.int("LGSVL__SIMULATOR_PORT", 8181)
LGSVL__AUTOPILOT_0_HOST = env.str("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
LGSVL__AUTOPILOT_0_PORT = env.int("LGSVL__AUTOPILOT_0_PORT", 9090)
TIME_LIMIT = 60  # seconds


def spawn_state(sim, index=0):
    state = lgsvl.AgentState()
    state.transform = sim.get_spawn()[index]
    return state


def place_car_on_the_point(state: lgsvl.AgentState, point: lgsvl.Vector, sim: lgsvl.Simulator) -> lgsvl.AgentState:
    state.transform = sim.map_point_on_lane(point)
    return state


class SimModel:
    @staticmethod
    def run(scenario, map: MapModel):
        sim = lgsvl.Simulator(LGSVL__SIMULATOR_HOST, LGSVL__SIMULATOR_PORT)

        sim.load(map.value[0])
        START_POINT = lgsvl.geometry.Vector(scenario.start[0], 0, scenario.start[1])
        ego_state = spawn_state(sim)
        ego_state = place_car_on_the_point(sim=sim, point=START_POINT, state=ego_state)

        ego = sim.add_agent("2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921", lgsvl.AgentType.EGO, ego_state)
        ego.connect_bridge(LGSVL__AUTOPILOT_0_HOST, LGSVL__AUTOPILOT_0_PORT)

        dv = lgsvl.dreamview.Connection(sim, ego, LGSVL__AUTOPILOT_0_HOST)
        dv.set_hd_map(map.value[1])
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
        try:
            t0 = time.time()
            while True:
                sim.run(0.5)
                currentPos = ego.state.position
                if lgsvl.evaluator.separation(currentPos, destination) < 5:
                    raise lgsvl.evaluator.TestException(
                        "PASSED: EGO does reach to destination, {} vs {}!".format(currentPos, destination)
                    )
                else:
                    if time.time() - t0 > TIME_LIMIT:
                        raise lgsvl.evaluator.TestException(
                            "Timeout! EGO does reach to destination, {} vs {}!".format(currentPos, destination)
                        )
        except lgsvl.evaluator.TestException as e:
            print("FAILED: {}".format(e))

        sim.close()
