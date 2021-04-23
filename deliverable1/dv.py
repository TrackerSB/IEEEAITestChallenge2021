import lgsvl
from common.scene import spawn_state
from environs import Env
from decouple import config

import logging
from common import SimConnection, EgoCarControl

FORMAT = "[%(levelname)6s] [%(name)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
log = logging.getLogger(__name__)

env = Env()

LGSVL__SIMULATOR_HOST = config("LGSVL__SIMULATOR_HOST")
LGSVL__SIMULATOR_PORT = int(config("LGSVL__SIMULATOR_PORT"))
LGSVL__APOLLO_HOST = config("LGSVL__APOLLO_HOST")
LGSVL__APOLLO_PORT = int(config("LGSVL__APOLLO_PORT"))
LGSVL__DREAMVIEW_HOST = config("LGSVL__DREAMVIEW_HOST")
LGSVL__DREAMVIEW_PORT = config("LGSVL__DREAMVIEW_PORT")

MAX_EGO_SPEED = 20  # (72 km/h, 45 mph)
MAX_POV_SPEED = 17.778  # (64 km/h, 40 mph)
INITIAL_HEADWAY = 150  # spec says >68m
SPEED_VARIANCE = 4
TIME_LIMIT = 10  # seconds
TIME_DELAY = 4
TARGET_POINT = lgsvl.Vector(103.947143554688, 0.00224405527114868, -1.90009093284607)


simConnection = SimConnection(timeout=5)
lgsvl_sim = simConnection.connect()
intial_state = spawn_state(lgsvl_sim)

# Place Ego Car - 5 meter ahead from the initial point
ego_state_a = EgoCarControl.place_ego_car_from_the_point(dimension="vertical", distance=5, state=intial_state)
# Ego Car goes straight
ego_state = EgoCarControl.drive_ego_car(state=ego_state_a, directions=[("vertical", 2), ("horizontal", -2)])
ego = lgsvl_sim.add_agent("Lincoln2017MKZ (Apollo 5.0)", lgsvl.AgentType.EGO, ego_state)
print(f'\nPoint A: {SimConnection.extract_position_from_state(ego_state_a)}')
simConnection.execute(ego_car=ego)
print(f'Point B: {SimConnection.extract_position_from_state(ego.state)}')
print(f'\nStarting driving by Apollo to Point C: {TARGET_POINT}')
# Start with Apollo
ego.connect_bridge(LGSVL__APOLLO_HOST, LGSVL__APOLLO_PORT)

dv = lgsvl.dreamview.Connection(lgsvl_sim, ego, LGSVL__DREAMVIEW_HOST, LGSVL__DREAMVIEW_PORT)
dv.set_hd_map("SingleLaneRoad")
dv.set_vehicle("Lincoln2017MKZ (Apollo 5.0)")

try:
    modules = env.list("LGSVL__AUTOPILOT_0_VEHICLE_MODULES", subcast=str)
    if len(modules) == 0:
        log.warning("LGSVL__AUTOPILOT_0_VEHICLE_MODULES is empty, using default list: {0}".format(modules))
        modules = [
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
except Exception:
    modules = [
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
    log.warning("LGSVL__AUTOPILOT_0_VEHICLE_MODULES is not set, using default list: {0}".format(modules))

destination = TARGET_POINT
dv.setup_apollo(destination.x, destination.z, modules)
simConnection.execute(ego_car=ego)