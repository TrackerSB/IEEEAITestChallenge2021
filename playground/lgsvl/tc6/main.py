from typing import Tuple, Optional, List

from lgsvl import AgentState, WalkWaypoint

from tc6.locations import *

# Test case configurable settings
EGO_SPEED: float = 50.0  # in km/h
EGO_DISTANCE: Optional[float] = None  # in m: None --> Calculate a distance which enforces a crash with the pedestrian
PEDESTRIAN_DIRECTION: bool = True  # Iff True (False) pedestrian moves from A to B (B to A)
TEST_PLACE: Location = LOC_2_VARB

# Test case fixed settings
UNIT_VECTOR: Vector = Vector(0, 0, 1)  # The unit vector with 0°
# NOTE Due to different bounding box sizes the crash positions of agents differ slightly
EGO_BBOX_OFFSET: float = 3  # in m
# NOTE The pedestrian speed is just an observation
PEDESTRIAN_SPEED: float = 4.4  # km/h # FIXME It seems like the pedestrian speed can not be changed


class _TestResult:
    successful: bool = True


class _PedestrianBehavior:
    def __init__(self, initial_state: AgentState, waypoints: List[WalkWaypoint]):
        self.initial_state = initial_state
        self.waypoints = waypoints

    initial_state: AgentState
    waypoints: List[WalkWaypoint]


def _generate_initial_pedestrian_behavior() -> _PedestrianBehavior:
    from common.geometry import get_directional_angle
    from common.scene import generate_initial_state
    from lgsvl.geometry import Spawn, Transform

    waypoints = [WalkWaypoint(TEST_PLACE.ped_crash_pos, 0)]
    if PEDESTRIAN_DIRECTION:
        start = TEST_PLACE.ped_pos_a
        finish = TEST_PLACE.ped_pos_b
    else:
        start = TEST_PLACE.ped_pos_b
        finish = TEST_PLACE.ped_pos_a
    rotation = get_directional_angle(start - finish, UNIT_VECTOR)
    spawn = Spawn(Transform(position=start, rotation=Vector(0, rotation, 0)))
    waypoints.append(WalkWaypoint(finish, 0))
    return _PedestrianBehavior(generate_initial_state(spawn, PEDESTRIAN_SPEED), waypoints)


def _generate_initial_ego_state(pedestrian_behavior: _PedestrianBehavior) -> Tuple[AgentState, float]:
    from common.geometry import rotate_around_y
    from common.scene import generate_initial_state
    from lgsvl.geometry import Spawn, Transform

    if EGO_DISTANCE is None:
        pedestrian_crash_distance = (pedestrian_behavior.initial_state.position - TEST_PLACE.ped_crash_pos).magnitude()
        time_to_crash_point = pedestrian_crash_distance / (PEDESTRIAN_SPEED / 3.6)  # in seconds
        ego_crash_distance = (EGO_SPEED / 3.6) * time_to_crash_point
    else:
        ego_crash_distance = EGO_DISTANCE
        time_to_crash_point = ego_crash_distance / (EGO_SPEED / 3.6)
    if TEST_PLACE.ego_approach_rotation is None:
        # Move in a 90° offset relative to the pedestrian movement
        ego_rotation_offset = 90 if PEDESTRIAN_DIRECTION else -90
        ego_rotation = pedestrian_behavior.initial_state.rotation.y + ego_rotation_offset
    else:
        ego_rotation = TEST_PLACE.ego_approach_rotation if PEDESTRIAN_DIRECTION else -TEST_PLACE.ego_approach_rotation
    ego_start_pos = TEST_PLACE.ped_crash_pos \
                    - rotate_around_y(UNIT_VECTOR * (ego_crash_distance + EGO_BBOX_OFFSET), -ego_rotation)
    ego_spawn = Spawn(Transform(position=ego_start_pos, rotation=Vector(0, ego_rotation, 0)))
    return generate_initial_state(ego_spawn, EGO_SPEED), time_to_crash_point


def _main() -> None:
    from common.scene import load_ego, load_scene, load_pedestrian, detect_collisions
    from common.simulator import connect_simulation
    from lgsvl.agent import Agent

    sim = connect_simulation("127.0.0.1", 8181)
    load_scene(sim, TEST_PLACE.map_name)

    pedestrian_behavior = _generate_initial_pedestrian_behavior()
    pedestrian = load_pedestrian(sim, TEST_PLACE.map_name, pedestrian_behavior.initial_state)
    pedestrian.follow(pedestrian_behavior.waypoints)

    initial_ego_state, time_to_crash_point = _generate_initial_ego_state(pedestrian_behavior)
    ego = load_ego(sim, "Jaguar2015XE (Apollo 5.0, many sensors)", initial_ego_state)

    test_result = _TestResult()

    def _on_collision(agent1: Agent, agent2: Agent, contact: Vector) -> None:
        test_result.successful = False
        sim.stop()

    detect_collisions(sim, _on_collision)

    sim.run(time_to_crash_point * 2)

    # FIXME Sometimes the following print is not visible on the console (but being in debug mode)
    print("Test succeeded" if test_result.successful else "Test failed")


if __name__ == "__main__":
    _main()
