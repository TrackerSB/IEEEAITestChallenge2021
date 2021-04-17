import time
import logging
from environs import Env
import lgsvl

FORMAT = "[%(levelname)6s] [%(name)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
log = logging.getLogger(__name__)

env = Env()

MAX_EGO_SPEED = 11.111  # (40 km/h, 25 mph)
MAX_POV_SPEED = 8.889  # (32 km/h, 20 mph)
INITIAL_HEADWAY = 130  # spec says >30m
SPEED_VARIANCE = 4
TIME_LIMIT = 30
TIME_DELAY = 3

LGSVL__SIMULATOR_HOST = env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1")
LGSVL__SIMULATOR_PORT = env.int("LGSVL__SIMULATOR_PORT", 8181)
LGSVL__AUTOPILOT_0_HOST = env.str("LGSVL__AUTOPILOT_0_HOST", "https://f55796af6ba7.ngrok.io/")
LGSVL__APOLLO_PORT = env.int("LGSVL__APOLLO_PORT", 8888)
LGSVL__DW_0_PORT = env.str("LGSVL__DW_0_PORT", "9090")



print("EOV_S_25_20 - ", end='')

sim = lgsvl.Simulator(LGSVL__SIMULATOR_HOST, LGSVL__SIMULATOR_PORT)
scene_name = "BorregasAve"
if sim.current_scene == scene_name:
    sim.reset()
else:
    sim.load(scene_name)

# spawn EGO in the 2nd to right lane
egoState = lgsvl.AgentState()
# A point close to the desired lane was found in Editor.
# This method returns the position and orientation of the closest lane to the point.
egoState.transform = sim.map_point_on_lane(lgsvl.Vector(-1.6, 0, -65))
ego = sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, egoState)
forward = lgsvl.utils.transform_to_forward(egoState.transform)
right = lgsvl.utils.transform_to_right(egoState.transform)

ego.connect_bridge(LGSVL__AUTOPILOT_0_HOST, LGSVL__APOLLO_PORT)

dv = lgsvl.dreamview.Connection(sim, ego, LGSVL__DW_0_PORT)