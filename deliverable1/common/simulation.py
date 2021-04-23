import lgsvl
import time
from lgsvl import Simulator
from decouple import config
from common.scene import load_scene


class SimConnection:
    def __init__(self, timeout: int = 10, scene: str = "SingleLaneRoad", load_scene: bool = True):
        self.timeout = timeout
        self.scene = scene
        self.load_scene = load_scene

    def execute(self, ego_car: lgsvl.agent.Agent):
        print(f'Second 0: {self.extract_position_from_state(ego_car.state)}')
        time_point = 1
        t0 = time.time()
        while True:
            self.sim.run(1)
            print(f'Second {time_point}: {self.extract_position_from_state(ego_car.state)}')
            time_point += 1
            if time.time() - t0 > self.timeout:
                break

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
        self.sim = Simulator(config("LGSVL__SIMULATOR_HOST"), int(config("LGSVL__SIMULATOR_PORT")))
        if self.load_scene:
            load_scene(self.sim, self.scene)
        return self.sim

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sim.close()
