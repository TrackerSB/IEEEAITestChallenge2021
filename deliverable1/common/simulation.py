import lgsvl
import time
from typing import Optional
from lgsvl import Simulator
from decouple import config
from common.scene import load_scene


class SimConnection:
    def __init__(self, scene: str = "SingleLaneRoad", load_scene: bool = True):
        self.scene = scene
        self.load_scene = load_scene

    def execute(self, vehicles: Optional[list] = [], timeout: int = 10, debug=False):
        if debug and len(vehicles) == 0:
            raise Exception("Debug Mode requires some vehicles to print the log!")
        time_point = 1
        t0 = time.time()
        if debug: self.debug_vehicles(f'Second {time_point}', vehicles)
        while True:
            self.sim.run(1)
            time_point += 1
            if debug: self.debug_vehicles(f'Second {time_point}', vehicles)
            if time.time() - t0 > timeout:
                break

    def debug_vehicles(self, message: str, vehicles: list):
        print(f'{message}:')
        for vehicle in vehicles:
            print(self.extract_position_from_state(vehicle.state))

    @staticmethod
    def extract_position_from_state(state: lgsvl.AgentState) -> lgsvl.Vector:
        return lgsvl.Vector(state.position.x, state.position.y, state.position.z)

    @staticmethod
    def extract_rotation_from_state(state: lgsvl.AgentState) -> lgsvl.Vector:
        return lgsvl.Vector(state.rotation.x, state.rotation.y, state.rotation.z)

    @staticmethod
    def connect_simulation(host: str, port: int) -> Simulator:
        return Simulator(address=host, port=port)

    def connect(self):
        self.sim = Simulator(config("LGSVL__SIMULATOR_HOST", default="127.0.0.1"),
                             int(config("LGSVL__SIMULATOR_PORT", default=8181)))
        if self.load_scene:
            load_scene(self.sim, self.scene)
        return self.sim

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sim.close()
