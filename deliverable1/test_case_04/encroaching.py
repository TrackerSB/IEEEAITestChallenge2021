from typing import Callable
import lgsvl
from common import SimConnection, CarControl


class Encroaching:
    def __init__(self, ego_speed: float, npc_speed: float,
                 sim_connection: SimConnection, setup_vehicles: Callable,
                 step: float, npc_waypoints: list):
        self.sedan = None
        self.ego = None
        self.npc_speed = npc_speed
        self.npc_waypoints = npc_waypoints
        self.ego_speed = ego_speed
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
        vehicles = self.setup_vehicles(self.simConnection, self.ego_speed)
        self.sedan = vehicles["sedan"]
        self.ego = vehicles["ego"]

        # Delay the simulator for 2 seconds
        self.simConnection.execute(timeout=2)

        self.sedan.on_collision(self.on_collision)
        self.ego.on_collision(self.on_collision)

        # Start the scenario
        waypoints = []
        for point in self.npc_waypoints:
            waypoints.append(lgsvl.DriveWaypoint(point, self.npc_speed, self.sedan.state.transform.rotation))

        self.sedan.follow(waypoints)
        self.simConnection.execute(timeout=15)

        print(f'Congratulation! A speed helps ago car avoiding crash is: {self.ego_speed} m/s')
        # Close the simulator
        self.simConnection.sim.close()

    def run(self):
        is_successful = False
        while is_successful is False:
            print(f'Starting NPC with the speed: {self.npc_speed} m/s and EGO with the speed: {self.ego_speed} m/s!')
            try:
                self.evaluate()
            except Exception:
                print(f'Ego collided with NPC! Restart the scenario...\n')
                self.ego_speed += self.step
                continue
            is_successful = True
