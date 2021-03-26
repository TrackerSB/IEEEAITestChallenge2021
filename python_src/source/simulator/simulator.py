import lgsvl


class Simulator:
    def __init__(self):
        # Connect to the simulator. Load the scene from http://localhost:8080/#/Maps
        sim = lgsvl.Simulator(address="localhost", port=8181)
        if sim.current_scene == "SingleLaneRoad":
            sim.reset()
        else:
            sim.load("SingleLaneRoad", seed=650387)
        self.sim = sim