from collections import namedtuple
from typing import Tuple, Optional

from lgsvl import AgentState, WalkWaypoint
from lgsvl.geometry import Vector

# Test case configurable settings
EGO_SPEED: float = 50.0  # in km/h
EGO_DISTANCE: Optional[float] = None  # in m: None --> Calculate a distance which enforces a crash with the pedestrian
PEDESTRIAN_DIRECTION: bool = False  # Iff True (False) pedestrian moves from A to B (B to A)

# Test location related settings
MAP_NAME: str = "San Francisco"
PEDESTRIAN_CRASH_POS: Vector = Vector(-202, 10.25, 139)
PEDESTRIAN_POS_A: Vector = Vector(-185, 10.25, 139)
PEDESTRIAN_POS_A_ROTATION: Vector = Vector(0, 270, 0)
PEDESTRIAN_POS_B: Vector = Vector(-205, 10.25, 139)

# Test case fixed settings
# NOTE Due to different bounding box sizes the crash positions of agents differ slightly
EGO_BBOX_OFFSET: float = 3  # in m
EGO_CRASH_POS: Vector = Vector(-202, 10.1, 142)
# NOTE The pedestrian speed is just an observation
PEDESTRIAN_SPEED: float = 4.5  # km/h # FIXME It seems like the pedestrian speed can not be changed


class _TestResult:
    successful: bool = True


PedestrianBehavior = namedtuple("PedestrianBehavior", "initialState waypoints")


def _generate_initial_pedestrian_behavior() -> PedestrianBehavior:
    from common.scene import generate_initial_state
    from lgsvl.geometry import Spawn, Transform

    waypoints = [WalkWaypoint(PEDESTRIAN_CRASH_POS, 0)]
    if PEDESTRIAN_DIRECTION:
        spawn = Spawn(Transform(position=PEDESTRIAN_POS_A, rotation=PEDESTRIAN_POS_A_ROTATION))
        waypoints.append(WalkWaypoint(PEDESTRIAN_POS_B, 0))
    else:
        spawn = Spawn(Transform(position=PEDESTRIAN_POS_B, rotation=Vector(0, 180, 0) + PEDESTRIAN_POS_A_ROTATION))
        waypoints.append(WalkWaypoint(PEDESTRIAN_POS_A, 0))
    return PedestrianBehavior(generate_initial_state(spawn, PEDESTRIAN_SPEED), waypoints)


def _generate_initial_ego_state(pedestrian_behavior: PedestrianBehavior) -> Tuple[AgentState, float]:
    from common.scene import generate_initial_state
    from lgsvl.geometry import Spawn, Transform

    if EGO_DISTANCE is None:
        pedestrian_crash_distance = (pedestrian_behavior.initialState.position - PEDESTRIAN_CRASH_POS).magnitude()
        time_to_crash_point = pedestrian_crash_distance / (PEDESTRIAN_SPEED / 3.6)  # in seconds
        ego_crash_distance = (EGO_SPEED / 3.6) * time_to_crash_point
    else:
        ego_crash_distance = EGO_DISTANCE
        time_to_crash_point = ego_crash_distance / (EGO_SPEED / 3.6)
    ego_spawn = Spawn(Transform(position=EGO_CRASH_POS + Vector(0, 0, ego_crash_distance),
                                rotation=PEDESTRIAN_POS_A_ROTATION - Vector(0, 90, 0)))
    return generate_initial_state(ego_spawn, EGO_SPEED), time_to_crash_point


def _main() -> None:
    from common.scene import load_ego, load_scene, load_pedestrian, detect_collisions
    from common.simulator import connect_simulation
    from lgsvl.agent import Agent

    sim = connect_simulation("127.0.0.1", 8181)
    load_scene(sim, MAP_NAME)

    pedestrian_behavior = _generate_initial_pedestrian_behavior()
    pedestrian = load_pedestrian(sim, MAP_NAME, pedestrian_behavior.initialState)
    pedestrian.follow(pedestrian_behavior.waypoints)

    initial_ego_state, time_to_crash_point = _generate_initial_ego_state(pedestrian_behavior)
    ego = load_ego(sim, "Jaguar2015XE (Apollo 5.0, many sensors)", initial_ego_state)

    test_result = _TestResult()

    def _on_collision(agent1: Agent, agent2: Agent, contact: Vector) -> None:
        test_result.successful = False
        sim.stop()

    detect_collisions(sim, _on_collision)

    sim.run(time_to_crash_point * 2)

    print("Test succeeded" if test_result.successful else "Test failed")


if __name__ == "__main__":
    _main()
