import lgsvl
import copy
from decouple import config
from common.scene import spawn_state
from common import SimConnection, CarControl
from common.scene import load_ego, load_npc
from common.apollo import ApolloModule, connect_to_dreamview

LGSVL__SIMULATOR_HOST = config("LGSVL__SIMULATOR_HOST")
LGSVL__SIMULATOR_PORT = int(config("LGSVL__SIMULATOR_PORT"))
LGSVL__APOLLO_HOST = config("LGSVL__APOLLO_HOST")
LGSVL__APOLLO_PORT = int(config("LGSVL__APOLLO_PORT"))
LGSVL__DREAMVIEW_HOST = config("LGSVL__DREAMVIEW_HOST")
LGSVL__DREAMVIEW_PORT = int(config("LGSVL__DREAMVIEW_PORT"))
TARGET_POINT = lgsvl.Vector(14.6010723114014, -0.00319436192512512, 1.21555626392365)


def init_configuration(lgsvl_sim: lgsvl.Simulator, initial_state: lgsvl.AgentState, npc_speed: float):
    # Init ego state
    ego_state = copy.deepcopy(initial_state)
    # Place Ego Car - 5 meter ahead from the initial point
    ego_state = CarControl.place_car_from_the_point(dimension="vertical", distance=5, state=ego_state)
    # Place Ego Car - 3.5m meter on the left
    ego_state = CarControl.place_car_from_the_point(dimension="horizontal", distance=-3.5, state=ego_state)
    # Drive ego car with speed 5m/s
    ego_state = CarControl.drive_ego_car(state=ego_state, directions=[("vertical", 5)], speed=2)
    # Add ego to simulator
    ego = load_ego(lgsvl_sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)

    # Init sedan state
    sedan_state = copy.deepcopy(initial_state)
    # Place Sedan - 5 meter ahead from the initial point
    sedan_state = CarControl.place_car_from_the_point(dimension="vertical", distance=5, state=sedan_state)
    # Add Sedan to simulator
    sedan = load_npc(lgsvl_sim, "Sedan", sedan_state)
    # Drive sedan follow its lane with given speed in m/s
    sedan.follow_closest_lane(True, npc_speed)

    # Init suv state
    suv_state = copy.deepcopy(initial_state)
    # Place SUV - 15 meter ahead from the initial point
    suv_state = CarControl.place_car_from_the_point(dimension="vertical", distance=20, state=suv_state)
    # Add suv to simulator
    suv = load_npc(lgsvl_sim, "SUV", suv_state)
    # Drive suv follow its lane with given speed in m/s
    suv.follow_closest_lane(True, npc_speed)
    return {
        "sedan": sedan,
        "suv": suv,
        "ego": ego,
    }


def drive_ego_with_apollo(simConnection: SimConnection):
    lgsvl_sim = simConnection.connect()
    initial_state = spawn_state(lgsvl_sim)  # Mutable object
    configuration = init_configuration(lgsvl_sim, initial_state, npc_speed=3.9)
    sedan = configuration["sedan"]
    ego = configuration["ego"]
    suv = configuration["suv"]

    # Run the simulator for 5 seconds with debug mode
    simConnection.execute(timeout=5)

    # Record collision if happen
    collisions = []

    def on_collision(agent1, agent2, contact):
        collisions.append([agent1, agent2, contact])
        print("{} collided with {}".format(agent1, agent2))

    sedan.on_collision(on_collision)
    suv.on_collision(on_collision)
    ego.on_collision(on_collision)

    # Drive ego to make lane change
    simConnection.execute(timeout=5)
    control = lgsvl.VehicleControl()
    control.steering = 0.037
    ego.apply_control(control, True)
    simConnection.execute(timeout=5)
    control.steering = -0.041
    ego.apply_control(control, True)
    simConnection.execute(timeout=5)

    # Start to drive the ego by Apollo
    try:
        dv_connection = connect_to_dreamview(ego, TARGET_POINT, LGSVL__APOLLO_HOST, LGSVL__APOLLO_PORT, LGSVL__DREAMVIEW_PORT)
        dv_connection.set_hd_map(config.test_place.map_name)
        dv_connection.enable_module(ApolloModule.Control.value)

        dv_connection.setup_apollo(TARGET_POINT.x, TARGET_POINT.z, [])
        return {
            "sedan": sedan,
            "suv": suv,
            "ego": ego,
            "collisions": collisions
        }
    except Exception:
        print("Failed to establish Apollo and DV connection!")
        simConnection.sim.close()


def drive_ego_no_apollo(simConnection: SimConnection, npc_speed: float):
    lgsvl_sim = simConnection.connect()
    initial_state = spawn_state(lgsvl_sim)  # Mutable object

    configuration = init_configuration(lgsvl_sim, initial_state, npc_speed=npc_speed)
    sedan = configuration["sedan"]
    ego = configuration["ego"]
    suv = configuration["suv"]

    # Run the simulator for 5 seconds with debug mode
    simConnection.execute(timeout=5, vehicles=[ego, sedan, suv], debug=True)

    # Record collision if happen
    collisions = []
    def on_collision(agent1, agent2, contact):
        collisions.append([agent1, agent2, contact])
        print("{} collided with {}".format(agent1, agent2))
    sedan.on_collision(on_collision)
    suv.on_collision(on_collision)
    ego.on_collision(on_collision)

    # Drive ego to make lane change
    simConnection.execute(timeout=5)
    control = lgsvl.VehicleControl()
    control.steering = 0.037
    ego.apply_control(control, True)
    simConnection.execute(timeout=5)
    control.steering = -0.041
    ego.apply_control(control, True)
    simConnection.execute(timeout=5)
    control.steering = 0
    ego.apply_control(control, True)
    simConnection.execute(timeout=7)
    control.braking = 1
    ego.apply_control(control, True)
    simConnection.execute(timeout=3)

    return {
        "sedan": sedan,
        "suv": suv,
        "ego": ego,
        "collisions": collisions
    }

