from typing import List, Tuple, Optional

from lgsvl import AgentState, WalkWaypoint
from lgsvl.geometry import Spawn, Transform, Vector

# Test case configurable settings
EGO_SPEED: float = 50.0  # in km/h
EGO_DISTANCE: Optional[float] = None  # in m: None --> Calculate a distance which enforces a crash with the pedestrian

# Test case fixed settings
MAP_NAME: str = "San Francisco"
EGO_ORIENTATION: Vector = Vector(0, 180, 0)
# NOTE Due to different bounding box sizes the crash positions of agents differ slightly
EGO_CRASH_POS: Vector = Vector(-202, 10.1, 142)
PEDESTRIAN_CRASH_POS: Vector = Vector(-202, 10.25, 139)
PEDESTRIAN_SPAWN: Spawn = Spawn(Transform(position=Vector(-185, 10.25, 139), rotation=Vector(0, -90, 0)))
PEDESTRIAN_DESTINATION: Vector = Vector(-205, 10.25, 139)
# NOTE The pedestrian speed is just an observation
PEDESTRIAN_SPEED: float = 4.5  # km/h # FIXME It seems like the pedestrian speed can not be changed


class _TestResult:
    successful: bool = True


def _generate_initial_pedestrian_state() -> AgentState:
    from common.scene import generate_initial_state

    return generate_initial_state(PEDESTRIAN_SPAWN, PEDESTRIAN_SPEED)


def _generate_pedestrian_waypoints() -> List[WalkWaypoint]:
    return [
        WalkWaypoint(PEDESTRIAN_CRASH_POS, 0),
        WalkWaypoint(PEDESTRIAN_DESTINATION, 0)
    ]


def _generate_initial_ego_state() -> Tuple[AgentState, float]:
    from common.scene import generate_initial_state

    pedestrian_crash_distance = (PEDESTRIAN_SPAWN.position - PEDESTRIAN_CRASH_POS).magnitude()
    if EGO_DISTANCE is None:
        time_to_crash_point = pedestrian_crash_distance / (PEDESTRIAN_SPEED / 3.6)  # in seconds
        ego_crash_distance = (EGO_SPEED / 3.6) * time_to_crash_point
    else:
        ego_crash_distance = EGO_DISTANCE
        time_to_crash_point = ego_crash_distance / (EGO_SPEED / 3.6)
    ego_spawn = Spawn(Transform(position=EGO_CRASH_POS + Vector(0, 0, ego_crash_distance), rotation=EGO_ORIENTATION))
    return generate_initial_state(ego_spawn, EGO_SPEED), time_to_crash_point


def _main() -> None:
    from common.scene import load_ego, load_scene, load_pedestrian, detect_collisions
    from common.simulator import connect_simulation
    from lgsvl.agent import Agent

    sim = connect_simulation("127.0.0.1", 8181)
    load_scene(sim, MAP_NAME)

    initial_ego_state, time_to_crash_point = _generate_initial_ego_state()
    ego = load_ego(sim, "Jaguar2015XE (Apollo 5.0, many sensors)", initial_ego_state)

    initial_pedestrian_state = _generate_initial_pedestrian_state()
    pedestrian = load_pedestrian(sim, MAP_NAME, initial_pedestrian_state)
    pedestrian.follow(_generate_pedestrian_waypoints())

    test_result = _TestResult()

    def _on_collision(agent1: Agent, agent2: Agent, contact: Vector) -> None:
        test_result.successful = False
        sim.stop()

    detect_collisions(sim, _on_collision)

    sim.run(time_to_crash_point * 2)

    print("Successful" if test_result.successful else "Failed")


if __name__ == "__main__":
    _main()
