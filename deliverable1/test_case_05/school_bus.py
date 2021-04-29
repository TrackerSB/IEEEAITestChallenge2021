import lgsvl
from lgsvl.geometry import Vector
from common import SimConnection, CarControl
from common.scene import load_ego, load_npc, spawn_state


class SchoolBus:
    def __init__(self, ego_speed: float, ego_target: Vector, ego_brake: float,
                 npc_speed: float, npc_source: Vector, npc_target: Vector,
                 sim_connection: SimConnection):
        self.ego_target = ego_target
        self.ego_speed = ego_speed
        self.ego_brake = ego_brake
        self.npc_speed = npc_speed
        self.npc_source = npc_source
        self.npc_target = npc_target
        self.collisions = []
        self.simConnection = sim_connection

    def on_collision(self, agent1, agent2, contact):
        self.collisions.append([agent1, agent2, contact])
        self.simConnection.sim.close()
        # print("Exception: {} collided with {}".format(agent1, agent2))
        raise Exception()

    def run(self):
        # Setup environment
        lgsvl_sim = self.simConnection.connect()
        control = lgsvl.NPCControl()
        ego_control = lgsvl.VehicleControl()

        # Placing the school_bus
        school_bus_state = spawn_state(lgsvl_sim)
        school_bus_state = CarControl.place_car_on_the_point(state=school_bus_state, sim=lgsvl_sim, point=self.npc_source)
        school_bus = load_npc(lgsvl_sim, "SchoolBus", school_bus_state)

        # Placing the ego on the starting point
        ego_state = spawn_state(lgsvl_sim)
        ego_state = CarControl.place_car_from_the_point(dimension="horizontal", distance=-6, state=ego_state)
        ego_state = CarControl.drive_ego_car(ego_state, [("vertical", self.ego_speed)])
        ego = load_ego(lgsvl_sim, "Lincoln2017MKZ (Apollo 5.0)", ego_state)

        # Callback collision function
        ego.on_collision(self.on_collision)
        school_bus.on_collision(self.on_collision)

        # Set waypoints for School Bus
        waypoints = []
        for point in [self.npc_source, self.npc_target]:
            waypoints.append(lgsvl.DriveWaypoint(point, self.npc_speed, school_bus.state.transform.rotation))

        try:
            # Start the scenario
            # The School Bus is parked on the street
            control.headlights = 2
            control.e_stop = True
            school_bus.apply_control(control)
            # Let the ego running for 2 seconds
            self.simConnection.execute(timeout=2)

            # The school bus turns on signal to prepare for the turn
            control.headlights = 0  # turn off headlight
            control.turn_signal_left = True
            school_bus.apply_control(control)
            self.simConnection.execute(timeout=2)

            # Brake the ego
            CarControl.brake_ego(ego=ego, control=ego_control, brake_value=self.ego_brake, sticky=True)

            # The school bus starts to turn right
            school_bus.follow(waypoints)
            self.simConnection.execute(timeout=10)
        except Exception:
            print("Failed!")
