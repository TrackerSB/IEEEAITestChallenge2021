import lgsvl
import os


class Simulator:
    def __init__(self, seconds=30, scene="SingleLaneRoad", error_message=None, load_scene=True):
        if error_message is None:
            error_message = 'test timed out after {}s.'.format(seconds)
        self.seconds = seconds
        self.error_message = error_message
        self.scene = scene
        self.load_scene = load_scene

    def __enter__(self):
        self.sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)
        if self.load_scene:
            if self.sim.current_scene == self.scene:
                self.sim.reset()
            else:
                self.sim.load(self.scene)
        return self.sim

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sim.close()


def spawn_state(sim, index=0):
    state = lgsvl.AgentState()
    state.transform = sim.get_spawn()[index]
    return state


def create_EGO(sim, state=None):  # Only create an EGO is none are already spawned
    if state is None:
        state = spawn_state(sim)
    return sim.add_agent("Jaguar2015XE (Apollo 3.0)", lgsvl.AgentType.EGO, state)


def create_NPC(sim, name, state=None):  # Create the specified NPC
    if state is None:
        state = spawn_state(sim)
    return sim.add_agent(name, lgsvl.AgentType.NPC, state)


def cm_equal(self, a, b, msg):  # Test vectors within 1cm
    self.assertAlmostEqual(a.x, b.x, 2, msg)
    self.assertAlmostEqual(a.y, b.y, 2, msg)
    self.assertAlmostEqual(a.z, b.z, 2, msg)
