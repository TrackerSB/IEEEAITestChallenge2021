import lgsvl
import time
import evaluator
from simulator import Simulator

MAX_EGO_SPEED = 11.18  # (40 km/h, 25 mph)
SPEED_VARIANCE = 10  # Simple Physics does not return an accurate value
MAX_POV_SPEED = 8.94  # (32 km/h, 20 mph)
TIME_LIMIT = 40  # seconds
TIME_DELAY = 3
MAX_FOLLOWING_DISTANCE = 50

print("TEST CASE 02")

sim = Simulator().sim

ego_state = lgsvl.AgentState()
ego_state.transform = sim.get_spawn()[0]
forward = lgsvl.utils.transform_to_forward(sim.get_spawn()[0])
# Agents can be spawned with a velocity. Default is to spawn with 0 velocity
ego = sim.add_agent("Jaguar2015XE (Autoware)", lgsvl.AgentType.EGO, ego_state)

c = lgsvl.VehicleControl()
c.throttle = 0.1
c.braking = 0
ego.apply_control(c, True)

POV_state = lgsvl.AgentState()
POV_state.transform.position = lgsvl.Vector(110, 0, 1.6)
POV_state.transform.rotation.y = -90
POV = sim.add_agent("Sedan", lgsvl.AgentType.NPC, POV_state)


def on_collision(agent1, agent2, contact):
    raise evaluator.TestException("Ego collided with {}".format(agent2))


ego.on_collision(on_collision)
POV.on_collision(on_collision)

try:
    t0 = time.time()
    sim.run(TIME_DELAY)  # The EGO should start moving first
    POV.follow_closest_lane(True, MAX_POV_SPEED, False)

    while True:
        sim.run(0.5)

        ego_cur_state = ego.state
        if ego_cur_state.speed > MAX_EGO_SPEED + SPEED_VARIANCE:
            raise evaluator.TestException("Ego speed exceeded limit, {} > {} m/s".format(ego_cur_state.speed, MAX_EGO_SPEED + SPEED_VARIANCE))

        POV_cur_state = POV.state
        if POV_cur_state.speed > MAX_POV_SPEED + SPEED_VARIANCE:
            raise evaluator.TestException(
                "POV speed exceeded limit, {} > {} m/s".format(POV_cur_state.speed, MAX_POV_SPEED + SPEED_VARIANCE))

        print(ego_cur_state.speed, MAX_POV_SPEED)
        if ego_cur_state.speed < MAX_POV_SPEED:
            c.throttle += 0.1
        else:
            c.throttle = 0
        ego.apply_control(c, True)

        if time.time() - t0 > TIME_LIMIT:
            break
except evaluator.TestException as e:
    print("FAILED: " + repr(e))
    exit()
