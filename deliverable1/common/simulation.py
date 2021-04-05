from lgsvl import Simulator


class SimConnection:
    def __init__(self, seconds=30, scene="BorregasAve", load_scene=True):
        self.seconds = seconds
        self.scene = scene
        self.load_scene = load_scene

    @staticmethod
    def connect_simulation(host: str, port: int) -> Simulator:
        return Simulator(address=host, port=port)

    def __enter__(self):
        from common.scene import load_scene
        LGSVL_HOST: str = "127.0.0.1"
        LGSVL_PORT: int = 8181
        self.sim = Simulator(LGSVL_HOST, LGSVL_PORT)
        if self.load_scene:
            load_scene(self.sim, self.scene)
        return self.sim

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sim.close()
