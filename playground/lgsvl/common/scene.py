from typing import Optional, Callable

from lgsvl import AgentState, Simulator
from lgsvl.agent import Agent, Pedestrian, EgoVehicle
from lgsvl.geometry import Spawn, Vector


def load_scene(sim: Simulator, scene_name: str) -> Spawn:
    if sim.current_scene == scene_name:
        sim.reset()
    else:
        sim.load(scene_name)

    return sim.get_spawn()[0]


def load_ego(sim: Simulator, ego_car_name: str, initial_state: AgentState) -> EgoVehicle:
    from lgsvl import AgentType
    from lgsvl.simulator import env

    return sim.add_agent(env.str("LGSVL__VEHICLE_0", ego_car_name), AgentType.EGO, initial_state)


def load_pedestrian(sim: Simulator, map_name: str, initial_state: AgentState) -> Pedestrian:
    from lgsvl import AgentType
    import random

    # The list of available pedestrians can be found in the maps PedestrianManager prefab
    # NOTE The availability of pedestrian names may depend on the currently used map
    allowed_names = [
        "Bob",
        "EntrepreneurFemale",
        "Howard",
        "Johny",
        "Pamela",
        "Presley",
        "Robin",
        "Stephen",
        "Zoe"
    ]
    return sim.add_agent(random.choice(allowed_names), AgentType.PEDESTRIAN, initial_state)


def add_random_traffic(sim: Simulator) -> None:
    from lgsvl import AgentType
    sim.add_random_agents(AgentType.NPC)
    sim.add_random_agents(AgentType.PEDESTRIAN)


def generate_initial_state(initial_pos: Spawn, initial_speed: Optional[float] = None) -> AgentState:
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
