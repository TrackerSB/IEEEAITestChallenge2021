from typing import Optional, Callable, List, Dict, Tuple

from lgsvl import AgentState, EgoVehicle, Simulator
from lgsvl.agent import Agent, Pedestrian
from lgsvl.geometry import Vector, Transform
from opendrive2lanelet.opendriveparser.elements.junction import Connection as ODConnection
from opendrive2lanelet.opendriveparser.elements.road import Road
from shapely.geometry import Point

from common.config import SupportedDreamViewCar, SupportedMap, SupportedNPC, SupportedPedestrian
from common.geometry import InterpolatedRoad


def load_scene(sim: Simulator, map: SupportedMap) -> Transform:
    if sim.current_scene == map.value[0]:
        sim.reset()
    else:
        sim.load(map.value[0], 650387)

    return sim.get_spawn()[0]


def load_ego(sim: Simulator, ego_car: SupportedDreamViewCar, initial_state: AgentState) -> EgoVehicle:
    from lgsvl import AgentType

    return sim.add_agent(ego_car.value, AgentType.EGO, initial_state)


def load_pedestrian(sim: Simulator, initial_state: AgentState) -> Pedestrian:
    from lgsvl import AgentType
    import random
    return sim.add_agent(random.choice(list(SupportedPedestrian)), AgentType.PEDESTRIAN, initial_state)


def load_npc(sim: Simulator, npc: SupportedNPC, initial_state: AgentState) -> Agent:
    from lgsvl import AgentType

    return sim.add_agent(npc.value, AgentType.NPC, initial_state)


def add_random_traffic(sim: Simulator) -> None:
    from lgsvl import AgentType
    # WARN Not all maps support both
    sim.add_random_agents(AgentType.NPC)
    sim.add_random_agents(AgentType.PEDESTRIAN)


def get_predefined_spawn_pos(sim, index=0) -> Transform:
    return sim.get_spawn()[index]


def get_entry_final_point(roads: Dict[int, InterpolatedRoad], connection: ODConnection,
                          distance: float) \
        -> Tuple[InterpolatedRoad, Transform, InterpolatedRoad, Transform]:
    from common.geometry import get_directional_angle
    connecting_road_id = connection.connectingRoad
    connecting_road = roads[connecting_road_id]
    connection_type = connection.contactPoint

    # Find start position
    moved_backward = 0
    current_index_on_road = 0
    current_road: InterpolatedRoad = roads[connecting_road_id]
    current_position = current_road.interpolated_points[current_index_on_road]
    while moved_backward < distance:
        if current_index_on_road <= 0:
            current_road = roads[current_road.link.predecessor.element_id]
            current_index_on_road = len(current_road.interpolated_points)
        current_index_on_road = current_index_on_road - 1
        next_position = current_road.interpolated_points[current_index_on_road]
        added_length = current_position.distance(next_position)
        moved_backward = moved_backward + added_length
        current_position = next_position

    start_pos = current_position
    start_segment = current_road
    start_road_points = start_segment.interpolated_points
    second_start_idx = max(current_index_on_road, 1)
    first_start_idx = second_start_idx - 1
    start_direction = Vector(start_road_points[second_start_idx].x - start_road_points[first_start_idx].x,
                             0,
                             start_road_points[second_start_idx].y - start_road_points[first_start_idx].y)
    start_angle = get_directional_angle(start_direction, Vector(0, 0, 1))

    # Find final position
    moved_forward = 0
    current_road: InterpolatedRoad = roads[connecting_road_id]
    current_index_on_road = len(current_road.interpolated_points) - 1
    current_position = current_road.interpolated_points[current_index_on_road]
    while moved_forward < distance:
        current_index_on_road = current_index_on_road + 1
        if current_index_on_road >= len(current_road.interpolated_points):
            current_road = roads[current_road.link.successor.element_id]
            current_index_on_road = 0
        next_position = current_road.interpolated_points[current_index_on_road]
        added_length = current_position.distance(next_position)
        moved_forward = moved_forward + added_length
        current_position = next_position

    final_pos = current_position
    final_segment = current_road
    final_road_points = final_segment.interpolated_points
    second_start_idx = max(current_index_on_road, 1)
    first_start_idx = second_start_idx - 1
    final_direction = Vector(final_road_points[second_start_idx].x - final_road_points[first_start_idx].x,
                             0,
                             final_road_points[second_start_idx].y - final_road_points[first_start_idx].y)
    final_angle = get_directional_angle(final_direction, Vector(0, 0, 1))

    return start_segment, Transform(
        position=Vector(start_pos.x, 0, start_pos.y),
        rotation=Vector(0, start_angle, 0)
    ), final_segment, Transform(
        position=Vector(final_pos.x, 0, final_pos.y),
        rotation=Vector(0, final_angle, 0)
    )


def generate_initial_state(initial_pos: Transform, initial_speed: Optional[float] = None) -> AgentState:
    """
    :param initial_speed: Initial speed in km/h
    """
    from lgsvl.utils import transform_to_forward
    movement = AgentState()
    movement.transform = initial_pos
    if initial_speed is not None:
        movement.velocity = (initial_speed / 3.6) * transform_to_forward(movement.transform)
    return movement


def _default_on_collision(agent1: Agent, agent2: Agent, contact: Vector) -> None:
    import logging
    name1 = agent1.uid if agent1 else "OBSTACLE"
    name2 = agent2.uid if agent1 else "OBSTACLE"
    logging.info("{} collided with {} at {}".format(name1, name2, contact))


def detect_collisions(sim: Simulator,
                      on_collision_detected: Callable[[Agent, Agent, Vector], None] = _default_on_collision) -> None:
    """
    NOTE This method should only be called after all agents were added to the given simulation.
    NOTE If the collision callback is not registered for ALL agents of the detected collision the simulation hangs.
    """
    for agent in sim.get_agents():
        agent.on_collision(on_collision_detected)
