from lgsvl import Simulator
from lgsvl.simulator import env


class SimConnection:
    def __init__(self, seconds=30, scene="BorregasAve", load_scene=True):
        self.seconds = seconds
        self.scene = scene
        self.load_scene = load_scene

    @staticmethod
    def _connect_simulation(host: str, port: int) -> Simulator:
        return Simulator(env.str("LGSVL__SIMULATOR_HOST", host),
                         env.int("LGSVL__SIMULATOR_PORT", port))

    def __enter__(self):
        LGSVL_HOST: str = "127.0.0.1"
        LGSVL_PORT: int = 8181
        self.sim = Simulator(LGSVL_HOST, LGSVL_PORT)
        if self.load_scene:
            if self.sim.current_scene == self.scene:
                self.sim.reset()
            else:
                self.sim.load(self.scene)
        return self.sim

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sim.close()


