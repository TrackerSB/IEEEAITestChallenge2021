from typing import Tuple, List, Optional

from lgsvl import AgentState, WalkWaypoint, Vector, Simulator

from test_case_06.config import TestConfig
from test_case_06.locations import Location

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
        from lgsvl.geometry import Transform

        waypoints = [WalkWaypoint(test_place.ped_crash_pos, 0)]
        if pedestrian_direction:
            start = test_place.ped_pos_a
            finish = test_place.ped_pos_b
        else:
            start = test_place.ped_pos_b
            finish = test_place.ped_pos_a
        rotation = get_directional_angle(finish - start, UNIT_VECTOR)
        spawn = Transform(position=start, rotation=Vector(0, rotation, 0))
        waypoints.append(WalkWaypoint(finish, 0))
        return _PedestrianBehavior(generate_initial_state(spawn, PEDESTRIAN_SPEED), waypoints)

    @staticmethod
    def _generate_initial_ego_state(pedestrian_behavior: _PedestrianBehavior, ego_distance: Optional[float],
                                    test_place: Location, ego_speed: float, pedestrian_direction: bool) \
            -> Optional[Tuple[AgentState, float]]:
        from common.geometry import rotate_around_y
        from common.scene import generate_initial_state
        from lgsvl.geometry import Transform

        if ego_distance is None:
            pedestrian_crash_distance = (
                        pedestrian_behavior.initial_state.position - test_place.ped_crash_pos).magnitude()
            time_to_crash_point = pedestrian_crash_distance / (PEDESTRIAN_SPEED / 3.6)  # in seconds
            ego_crash_distance = (ego_speed / 3.6) * time_to_crash_point
        else:
            ego_crash_distance = ego_distance
            time_to_crash_point = ego_crash_distance / (ego_speed / 3.6)
        if ego_crash_distance <= test_place.max_ego_distance:
            if test_place.ego_approach_rotation is None:
                # Move in a 90° offset relative to the pedestrian movement
                ego_rotation_offset = -90 if pedestrian_direction else 90
                ego_rotation = pedestrian_behavior.initial_state.rotation.y + ego_rotation_offset
            else:
                ego_rotation = -test_place.ego_approach_rotation if pedestrian_direction else test_place.ego_approach_rotation
            ego_start_pos = test_place.ped_crash_pos \
                            - rotate_around_y(UNIT_VECTOR * (ego_crash_distance + EGO_BBOX_OFFSET), -ego_rotation)
            ego_spawn = Transform(position=ego_start_pos, rotation=Vector(0, ego_rotation, 0))
            return generate_initial_state(ego_spawn, ego_speed), time_to_crash_point
        else:
            return None

    @staticmethod
    def execute(sim: Simulator, config: TestConfig) -> Optional[bool]:
        import logging
        from common.apollo import ApolloModule, connect_to_dreamview
        from common.scene import load_ego, load_scene, load_pedestrian, detect_collisions
        from lgsvl.agent import Agent
        from time import time

        load_scene(sim, config.test_place.map_name)

        pedestrian_behavior = TestCase6._generate_initial_pedestrian_behavior(
            config.test_place, config.pedestrian_direction)
        pedestrian = load_pedestrian(sim, config.test_place.map_name, pedestrian_behavior.initial_state)
        pedestrian.follow(pedestrian_behavior.waypoints)

        ego_state_result = TestCase6._generate_initial_ego_state(
            pedestrian_behavior, config.ego_distance, config.test_place, config.ego_speed, config.pedestrian_direction)
        if ego_state_result is None:
            logging.warning("Could not generate initial ego state within allowed parameter range")
            return None
        else:
            initial_ego_state, time_to_crash_point = ego_state_result
            ego = load_ego(sim, config.ego_car_name, initial_ego_state)

            dv_connection = connect_to_dreamview(ego, config.test_place.ped_crash_pos, "localhost", 9090, 8888)
            dv_connection.set_hd_map(config.test_place.map_name)
            dv_connection.enable_module(ApolloModule.Control.value)

            test_result = _TestResult()

            def _on_collision(agent1: Agent, agent2: Agent, contact: Vector) -> None:
                test_result.successful = False

            detect_collisions(sim, _on_collision)

            start_time = time()

            running_simulation_failed_once = False
            while (time() - start_time) < (time_to_crash_point * 2) and test_result.successful:
                try:
                    sim.run(1)
                    if running_simulation_failed_once:
                        logging.info("Continuing the execution failed once but could be restarted")
                    running_simulation_failed_once = False
                except Exception:
                    if running_simulation_failed_once:
                        logging.exception("Continuing the execution failed again. Skipping test.")
                        return None
                    else:
                        logging.exception("Continuing the execution failed. Retrying once.")
                        running_simulation_failed_once = True

            # FIXME Sometimes the following print is not visible on the console (but being in debug mode)
            return test_result.successful
