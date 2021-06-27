import lgsvl
import numpy

class TestException(Exception):
    pass


def right_lane_check(simulator, ego_transform):
    egoLane = simulator.map_point_on_lane(ego_transform.position)
    right = lgsvl.utils.transform_to_right(ego_transform)
    rightLane = simulator.map_point_on_lane(ego_transform.position + 3.6 * right)

    return almost_equal(egoLane.position.x, rightLane.position.x) and \
        almost_equal(egoLane.position.y, rightLane.position.y) and \
        almost_equal(egoLane.position.z, rightLane.position.z)


def in_parking_zone(beginning, end, ego_transform):
    forward = lgsvl.utils.transform_to_forward(ego_transform)
    b2e = ego_transform.position - beginning  # Vector from beginning of parking zone to EGO's position
    b2e = b2e * (1 / b2e.magnitude())  # Make it a Unit vector to simplify dot product result
    e2e = end - ego_transform.position  # Vector from EGO's position to end of parking zone
    e2e = e2e * (1 / e2e.magnitude())
    return (
        numpy.dot([forward.x, forward.y, forward.z], [b2e.x, b2e.y, b2e.z]) > 0.9
        and numpy.dot([forward.x, forward.y, forward.z], [e2e.x, e2e.y, e2e.z]) > 0.9
    )


def almost_equal(a, b, diff=0.5):
    return abs(a - b) <= diff


def separation(V1, V2):
    return (V1 - V2).magnitude()

if __name__ == "__main__":
    from environs import Env
    from common import CarControl
    import lgsvl
    import time

    MAX_EGO_SPEED = 29.06  # (105 km/h, 65 mph)
    SPEED_VARIANCE = 10  # Simple Physics does not return an accurate value
    MAX_POV_SPEED = 26.82  # (96 km/h, 60 mph)
    MAX_POV_ROTATION = 5  # deg/s
    TIME_LIMIT = 30  # seconds
    TIME_DELAY = 5
    MAX_FOLLOWING_DISTANCE = 110  # Apollo 3.5 is very cautious

    env = Env()

    LGSVL__SIMULATOR_HOST = env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1")
    LGSVL__SIMULATOR_PORT = env.int("LGSVL__SIMULATOR_PORT", 8181)
    LGSVL__AUTOPILOT_0_HOST = env.str("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
    LGSVL__AUTOPILOT_0_PORT = env.int("LGSVL__AUTOPILOT_0_PORT", 9090)

    sim = lgsvl.Simulator(LGSVL__SIMULATOR_HOST, LGSVL__SIMULATOR_PORT)

    sim.load("CubeTown")

    spawns = sim.get_spawn()

    state = lgsvl.AgentState()
    state.transform = spawns[0]

    ego = sim.add_agent("2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921", lgsvl.AgentType.EGO, state)
    ego.connect_bridge(LGSVL__AUTOPILOT_0_HOST, LGSVL__AUTOPILOT_0_PORT)

    dv = lgsvl.dreamview.Connection(sim, ego, LGSVL__AUTOPILOT_0_HOST)
    dv.set_hd_map('Cubetown')
    dv.set_vehicle('Lincoln2017MKZ LGSVL')

    modules = [
        'Localization',
        'Transform',
        'Routing',
        'Prediction',
        'Planning',
        'Control'
    ]
    destination = spawns[0].destinations[0]
    dv.setup_apollo(destination.position.x, destination.position.z, modules)
    endOfRoad = destination


    POVState = lgsvl.AgentState()
    sedan_state = POVState
    sedan_state = CarControl.place_car_from_the_point(dimension="vertical", distance=25, state=sedan_state)
    sedan_state = CarControl.place_car_from_the_point(dimension="horizontal", distance=-3, state=sedan_state)
    sedan_state = CarControl.rotate_car_by_degree(state=sedan_state, degree=180)
    POV = sim.add_agent("Sedan", lgsvl.AgentType.NPC, sedan_state)


    def on_collision(agent1, agent2, contact):
        raise lgsvl.evaluator.TestException("Ego collided with {}".format(agent2))

    ego.on_collision(on_collision)
    POV.on_collision(on_collision)

    try:
        t0 = time.time()
        sim.run(5)  # The EGO should start moving first
        POV.follow_closest_lane(True, MAX_POV_SPEED, False)
        while True:
            sim.run(0.5)
            egoCurrentState = ego.state
            if egoCurrentState.speed > MAX_EGO_SPEED + SPEED_VARIANCE:
                raise lgsvl.evaluator.TestException(
                    "Ego speed exceeded limit, {} > {} m/s".format(egoCurrentState.speed,
                                                                   MAX_EGO_SPEED + SPEED_VARIANCE)
                )
            POVCurrentState = POV.state
            if POVCurrentState.speed > MAX_POV_SPEED + SPEED_VARIANCE:
                raise lgsvl.evaluator.TestException(
                    "POV speed exceeded limit, {} > {} m/s".format(POVCurrentState.speed,
                                                                   MAX_POV_SPEED + SPEED_VARIANCE)
                )
            if POVCurrentState.angular_velocity.y > MAX_POV_ROTATION:
                raise lgsvl.evaluator.TestException(
                    "POV angular rotation exceeded limit, {} > {} deg/s".format(
                        POVCurrentState.angular_velocity, MAX_POV_ROTATION
                    )
                )
            if time.time() - t0 > TIME_LIMIT:
                break
    except lgsvl.evaluator.TestException as e:
        exit("FAILED: {}".format(e))

    separation = lgsvl.evaluator.separation(egoCurrentState.position, POVCurrentState.position)
    try:
        if separation > MAX_FOLLOWING_DISTANCE:
            raise lgsvl.evaluator.TestException(
                "FAILED: EGO following distance was not maintained, {} > {}".format(separation, MAX_FOLLOWING_DISTANCE)
            )
        else:
            print("PASSED")
    except lgsvl.evaluator.TestException as e:
        exit("FAILED: {}".format(e))