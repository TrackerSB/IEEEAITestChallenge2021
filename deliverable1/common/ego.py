import lgsvl
from common.simulation import SimConnection


class CarControl:
    def drive_ego_car(state: lgsvl.AgentState, directions: list = []):
        for d in directions:
            speed = d[1]
            direction = lgsvl.Vector(0, 0, 0, )
            if d[0] == "vertical":
                direction = lgsvl.utils.transform_to_forward(state.transform)
            elif d[0] == "horizontal":
                direction = lgsvl.utils.transform_to_right(state.transform)
            state.velocity += speed * direction
        return state

    def place_car_from_the_point(state: lgsvl.AgentState, dimension: str = "vertical", distance: float = 1,
                                     debug: bool = False):
        direction = lgsvl.Vector(0, 0, 0, )
        if dimension == "vertical":
            direction = lgsvl.utils.transform_to_forward(state.transform)
        elif dimension == "horizontal":
            direction = lgsvl.utils.transform_to_right(state.transform)
        if debug: print(f'Old position: {SimConnection.extract_position_from_state(state)}')
        state.transform.position = state.position + (distance * direction)
        if debug: print(f'New position: {SimConnection.extract_position_from_state(state)}')
        return state
