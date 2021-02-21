from typing import Optional

from lgsvl import AgentState, EgoVehicle, Simulator
from lgsvl.agent import Agent
from lgsvl.geometry import Spawn


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


def add_random_traffic(sim: Simulator) -> None:
    from lgsvl import AgentType
    sim.add_random_agents(AgentType.NPC)
    sim.add_random_agents(AgentType.PEDESTRIAN)


def generate_initial_state(initial_pos: Spawn, initial_speed: Optional[int] = None) -> AgentState:
    from lgsvl.utils import transform_to_forward
    movement = AgentState()
    movement.transform = initial_pos
    if initial_speed is not None:
        movement.velocity = initial_speed * transform_to_forward(movement.transform)
    return movement


def detect_collisions(agent: Agent) -> None:
    def on_collision_detected(agent1: Agent, agent2: Agent, contact) -> None:
        name1 = agent1.uid if agent1 else "OBSTACLE"
        name2 = agent2.uid if agent1 else "OBSTACLE"
        print("{} collided with {} at {}".format(name1, name2, contact))

    agent.on_collision(on_collision_detected)
