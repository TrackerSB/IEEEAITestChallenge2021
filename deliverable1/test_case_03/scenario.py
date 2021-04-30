import lgsvl
from common import SimConnection, CarControl
from common.scene import load_ego, load_npc, spawn_state

COLLISIONS = []


class Scenario:
    def __init__(self, sim_connection: SimConnection):
        self.sim_connection = sim_connection

    def on_collision(self, agent1, agent2, contact):
        COLLISIONS.append([agent1, agent2, contact])
        print("Exception: {} collided with {}".format(agent1.name, agent2.name))
        raise Exception()

    def generate_vehicles(self, sim: lgsvl.Simulator, vehicles: list):
        agents = []
        for vehicle in vehicles:
            state = spawn_state(sim)
            state = CarControl.place_car_from_the_point(dimension="vertical", distance=vehicle["distance"], state=state)
            agent = vehicle["load_vehicle"](sim, vehicle["type"], state)
            agent.on_collision(self.on_collision)
            agents.append(agent)
        return agents

    @staticmethod
    def drive_ego(sim_connection: SimConnection, ego: lgsvl.agent.EgoVehicle):
        control = lgsvl.VehicleControl()
        control.steering = -0.4
        control.throttle = 0.2
        ego.apply_control(control, True)
        sim_connection.execute(timeout=3)
        control.steering = 0.13
        ego.apply_control(control, True)
        sim_connection.execute(timeout=3)
        control.steering = 0
        ego.apply_control(control, True)
        sim_connection.execute(timeout=5)
