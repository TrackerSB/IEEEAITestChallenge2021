import lgsvl


def spawn_state(sim, index=0):
    state = lgsvl.AgentState()
    state.transform = sim.get_spawn()[index]
    return state


def place_car_on_the_point(state: lgsvl.AgentState, point: lgsvl.Vector, sim: lgsvl.Simulator) -> lgsvl.AgentState:
    state.transform = sim.map_point_on_lane(point)
    return state


def load_npc(sim: lgsvl.Simulator, NPC_car_name: str, initial_state: lgsvl.AgentState) -> lgsvl.agent.Agent:
    from lgsvl import AgentType
    # name: Sedan, SUV, Jeep, Hatchback, SchoolBus, BoxTruck

    return sim.add_agent(NPC_car_name, AgentType.NPC, initial_state)


def place_car_from_the_point(state: lgsvl.AgentState, dimension: str = "vertical",
                             distance: float = 1) -> lgsvl.AgentState:
    direction = lgsvl.Vector(0, 0, 0, )
    if dimension == "vertical":
        direction = lgsvl.utils.transform_to_forward(state.transform)
    elif dimension == "horizontal":
        direction = lgsvl.utils.transform_to_right(state.transform)
    state.transform.position = state.position + (distance * direction)
    return state
