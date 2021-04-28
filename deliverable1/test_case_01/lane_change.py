import lgsvl
from typing import Callable
from common import SimConnection, CarControl

class LaneChange:
    def __init__(self, npc_speed: float, sim_connection: SimConnection, setup_vehicles: Callable, step: float):
        self.sedan = None
        self.suv = None
        self.ego = None
        self.npc_speed = npc_speed
        self.simConnection = sim_connection
        self.collisions = []
        self.setup_vehicles = setup_vehicles
        self.step = step

    def on_collision(self, agent1, agent2, contact):
        self.collisions.append([agent1, agent2, contact])
        self.simConnection.sim.close()
        print("Exception: {} collided with {}".format(agent1, agent2))
        raise Exception()

    def evaluate(self):
        # Setup vehicles
        vehicles = self.setup_vehicles(self.simConnection, self.npc_speed)
        self.sedan = vehicles["sedan"]
        self.suv = vehicles["suv"]
        self.ego = vehicles["ego"]

        # Run the simulator for 5 seconds
        self.simConnection.execute(timeout=5)

        self.sedan.on_collision(self.on_collision)
        self.suv.on_collision(self.on_collision)
        self.ego.on_collision(self.on_collision)

        # Drive ego to make lane change
        self.simConnection.execute(timeout=5)
        control = lgsvl.VehicleControl()
        control.steering = 0.037
        self.ego.apply_control(control, True)
        self.simConnection.execute(timeout=5)
        control.steering = -0.041
        self.ego.apply_control(control, True)
        self.simConnection.execute(timeout=5)
        control.steering = 0
        self.ego.apply_control(control, True)
        self.simConnection.execute(timeout=7)
        control.braking = 1
        self.ego.apply_control(control, True)
        self.simConnection.execute(timeout=3)

        if (self.suv.state.position.x < self.ego.state.position.x < self.sedan.state.position.x) is False:
            print("Exception: An ego car not between Sedan and SUV!")
            raise Exception()

        if abs(self.sedan.state.position.z - self.ego.state.position.z) > 1.5:
            print("Exception: Sedan and Ego not on same lane!")
            raise Exception()

        if abs(self.suv.state.position.z - self.ego.state.position.z) > 1.5:
            print("Exception: SUV and Ego not on same lane!")
            raise Exception()

        print(f'Congratulation! Final NPCs speed is: {self.npc_speed}')
        # Close the simulator
        self.simConnection.sim.close()

    def run(self):
        is_successful = False
        while is_successful is False:
            print(f'Starting NPCs with the speed: {self.npc_speed} m/s!')
            try:
                self.evaluate()
            except Exception:
                print(f'Changing Lane failed! Restart the scenario...\n')
                self.npc_speed += self.step
                continue
            is_successful = True
