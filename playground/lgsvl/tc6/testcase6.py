from typing import Tuple, List, Optional

from lgsvl import AgentState, WalkWaypoint, Vector, Simulator

from tc6.config import TestConfig
from tc6.locations import Location

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


class TestCase6:
    @staticmethod
    def _generate_initial_pedestrian_behavior(test_place: Location, pedestrian_direction: bool) -> _PedestrianBehavior:
        from common.geometry import get_directional_angle
        from common.scene import generate_initial_state
        from lgsvl.geometry import Spawn, Transform

        waypoints = [WalkWaypoint(test_place.ped_crash_pos, 0)]
        if pedestrian_direction:
            start = test_place.ped_pos_a
            finish = test_place.ped_pos_b
        else:
            start = test_place.ped_pos_b
            finish = test_place.ped_pos_a
        rotation = get_directional_angle(finish - start, UNIT_VECTOR)
        spawn = Spawn(Transform(position=start, rotation=Vector(0, rotation, 0)))
        waypoints.append(WalkWaypoint(finish, 0))
        return _PedestrianBehavior(generate_initial_state(spawn, PEDESTRIAN_SPEED), waypoints)

    @staticmethod
    def _generate_initial_ego_state(pedestrian_behavior: _PedestrianBehavior, ego_distance: Optional[float],
                                    test_place: Location, ego_speed: float, pedestrian_direction: bool) \
            -> Tuple[AgentState, float]:
        from common.geometry import rotate_around_y
        from common.scene import generate_initial_state
        from lgsvl.geometry import Spawn, Transform

        if ego_distance is None:
            pedestrian_crash_distance = (
                        pedestrian_behavior.initial_state.position - test_place.ped_crash_pos).magnitude()
            time_to_crash_point = pedestrian_crash_distance / (PEDESTRIAN_SPEED / 3.6)  # in seconds
            ego_crash_distance = (ego_speed / 3.6) * time_to_crash_point
        else:
            ego_crash_distance = ego_distance
            time_to_crash_point = ego_crash_distance / (ego_speed / 3.6)
        if test_place.ego_approach_rotation is None:
            # Move in a 90° offset relative to the pedestrian movement
            ego_rotation_offset = -90 if pedestrian_direction else 90
            ego_rotation = pedestrian_behavior.initial_state.rotation.y + ego_rotation_offset
        else:
            ego_rotation = -test_place.ego_approach_rotation if pedestrian_direction else test_place.ego_approach_rotation
        ego_start_pos = test_place.ped_crash_pos \
                        - rotate_around_y(UNIT_VECTOR * (ego_crash_distance + EGO_BBOX_OFFSET), -ego_rotation)
        ego_spawn = Spawn(Transform(position=ego_start_pos, rotation=Vector(0, ego_rotation, 0)))
        return generate_initial_state(ego_spawn, ego_speed), time_to_crash_point

    @staticmethod
    def execute(sim: Simulator, config: TestConfig) -> bool:
        from common.scene import load_ego, load_scene, load_pedestrian, detect_collisions
        from lgsvl.agent import Agent
        from time import time

        load_scene(sim, config.test_place.map_name)

        pedestrian_behavior = TestCase6._generate_initial_pedestrian_behavior(
            config.test_place, config.pedestrian_direction)
        pedestrian = load_pedestrian(sim, config.test_place.map_name, pedestrian_behavior.initial_state)
        pedestrian.follow(pedestrian_behavior.waypoints)

        initial_ego_state, time_to_crash_point = TestCase6._generate_initial_ego_state(
            pedestrian_behavior, config.ego_distance, config.test_place, config.ego_speed, config.pedestrian_direction)
        ego = load_ego(sim, config.ego_car_name, initial_ego_state)

        test_result = _TestResult()

        def _on_collision(agent1: Agent, agent2: Agent, contact: Vector) -> None:
            test_result.successful = False

        detect_collisions(sim, _on_collision)

        start_time = time()
        while (time() - start_time) < (time_to_crash_point * 2) and test_result.successful:
            sim.run(1)

        # FIXME Sometimes the following print is not visible on the console (but being in debug mode)
        return test_result.successful
