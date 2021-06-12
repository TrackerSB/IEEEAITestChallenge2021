from enum import auto, unique
from typing import Optional, Callable

from lgsvl import AgentState, EgoVehicle, Simulator
from lgsvl.agent import Agent, Pedestrian
from lgsvl.geometry import Vector, Transform

from common.utility import AutoName


@unique
class SupportedMap(AutoName):
    SanFrancisco = auto()
    Shalun = auto()


@unique
class SupportedNPC(AutoName):
    BoxTruck = auto()
    Hatchback = auto()
    Jeep = auto()
    SchoolBus = auto()
    Sedan = auto()
    SUV = auto()


# The list of available pedestrians can be found in the maps PedestrianManager prefab
# NOTE The availability of pedestrian names may depend on the currently used map
@unique
class SupportedPedestrian(AutoName):
    Bob = auto()
    EntrepreneurFemale = auto()
    Howard = auto()
    Johny = auto()
    Pamela = auto()
    Presley = auto()
    Robin = auto()
    Stephen = auto()
    Zoe = auto()


def load_scene(sim: Simulator, map: SupportedMap) -> Transform:
    if sim.current_scene == map.value:
        sim.reset()
    else:
        sim.load(map.value, 650387)

    return sim.get_spawn()[0]


def load_ego(sim: Simulator, ego_car_config_name: str, initial_state: AgentState) -> EgoVehicle:
    from lgsvl import AgentType

    return sim.add_agent(ego_car_config_name, AgentType.EGO, initial_state)


def load_pedestrian(sim: Simulator, initial_state: AgentState) -> Pedestrian:
    from lgsvl import AgentType
    import random
    return sim.add_agent(random.choice(list(SupportedPedestrian)), AgentType.PEDESTRIAN, initial_state)


def load_npc(sim: Simulator, npc: SupportedNPC, initial_state: AgentState) -> Agent:
    from lgsvl import AgentType

    return sim.add_agent(npc.value, AgentType.NPC, initial_state)


def add_random_traffic(sim: Simulator) -> None:
    from lgsvl import AgentType
    sim.add_random_agents(AgentType.NPC)
    # sim.add_random_agents(AgentType.PEDESTRIAN)  # FIXME Seems not to work


def get_predefined_spawn_pos(sim, index=0) -> Transform:
    return sim.get_spawn()[index]


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
