import lgsvl
from common.simulation import SimConnection


class CarControl:
    @staticmethod
    def drive_ego_car(state: lgsvl.AgentState, directions: list = []) -> lgsvl.AgentState:
        for d in directions:
            speed = d[1]
            direction = lgsvl.Vector(0, 0, 0, )
            if d[0] == "vertical":
                direction = lgsvl.utils.transform_to_forward(state.transform)
            elif d[0] == "horizontal":
                direction = lgsvl.utils.transform_to_right(state.transform)
            state.velocity += speed * direction
        return state

    @staticmethod
    def place_car_from_the_point(state: lgsvl.AgentState, dimension: str = "vertical", distance: float = 1,
                                     debug: bool = False) -> lgsvl.AgentState:
        direction = lgsvl.Vector(0, 0, 0, )
        if dimension == "vertical":
            direction = lgsvl.utils.transform_to_forward(state.transform)
        elif dimension == "horizontal":
            direction = lgsvl.utils.transform_to_right(state.transform)
        if debug: print(f'Old position: {SimConnection.extract_position_from_state(state)}')
        state.transform.position = state.position + (distance * direction)
        if debug: print(f'New position: {SimConnection.extract_position_from_state(state)}')
        return state

    @staticmethod
    def place_car_on_the_point(state: lgsvl.AgentState, point: lgsvl.Vector, sim: lgsvl.Simulator) -> lgsvl.AgentState:
        state.transform = sim.map_point_on_lane(point)
        return state

    @staticmethod
    def rotate_car_by_degree(state: lgsvl.AgentState, degree: float) -> lgsvl.AgentState:
        state.transform.rotation.y = degree
        return state

    @staticmethod
    def brake_ego(ego: lgsvl.agent.EgoVehicle, control: lgsvl.VehicleControl, brake_value: float, sticky: bool = False):
        control.braking = brake_value
        ego.apply_control(control, sticky)

    @staticmethod
    def throttle_ego(ego: lgsvl.agent.EgoVehicle, control: lgsvl.VehicleControl, throttle_value: float, sticky: bool = False):
        control.throttle = throttle_value
        ego.apply_control(control, sticky)