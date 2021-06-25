from typing import Optional, Callable, List, Dict, Tuple

from lgsvl import AgentState, EgoVehicle, Simulator
from lgsvl.agent import Agent, Pedestrian
from lgsvl.geometry import Vector, Transform
from opendrive2lanelet.opendriveparser.elements.junction import Connection as ODConnection
from shapely.geometry import Point

from common.config import SupportedDreamViewCar, SupportedMap, SupportedNPC, SupportedPedestrian


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


def get_entry_final_point(road_points: Dict[int, List[Point]], connection: ODConnection) -> Tuple[Transform, Transform]:
    from common.geometry import get_directional_angle
    connecting_road_id = connection.connectingRoad
    connecting_road = road_points[connecting_road_id]
    connection_type = connection.contactPoint

    segment_start_point = connecting_road[0]
    segment_start_direction = Vector(connecting_road[1].x - connecting_road[0].x,
                                     0,
                                     connecting_road[1].y - connecting_road[0].y)
    segment_start_angle = get_directional_angle(segment_start_direction, Vector(0, 0, 1))

    segment_final_point = connecting_road[-1]
    segment_final_direction = Vector(connecting_road[-1].x - connecting_road[-2].x,
                                     0,
                                     connecting_road[-1].y - connecting_road[-2].y)
    segment_final_angle = get_directional_angle(segment_final_direction, Vector(0, 0, 1))

    if connection_type == "start":
        junction_start_point = segment_start_point
        junction_start_angle = segment_start_angle
        junction_final_point = segment_final_point
        junction_final_angle = segment_final_angle
    else:
        junction_start_point = segment_final_point
        junction_start_angle = segment_final_angle
        junction_final_point = segment_start_point
        junction_final_angle = segment_start_angle

    return Transform(
        position=Vector(junction_start_point.x, 0, junction_start_point.y),
        rotation=Vector(0, junction_start_angle, 0)
    ), Transform(
        position=Vector(junction_final_point.x, 0, junction_final_point.y),
        rotation=Vector(0, junction_final_angle, 0)
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
