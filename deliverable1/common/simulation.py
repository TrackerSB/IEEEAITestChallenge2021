from lgsvl import Simulator
from decouple import config
from common.scene import load_scene


class SimConnection:
    def __init__(self, seconds=30, scene="BorregasAve", load_scene=True):
        self.seconds = seconds
        self.scene = scene
        self.load_scene = load_scene

    @staticmethod
    def connect_simulation(host: str, port: int) -> Simulator:
        return Simulator(address=host, port=port)

    def __enter__(self):
        self.sim = Simulator(config("LGSVL__SIMULATOR_HOST"), int(config("LGSVL__SIMULATOR_PORT")))
        if self.load_scene:
            load_scene(self.sim, self.scene)
        return self.sim

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sim.close()
