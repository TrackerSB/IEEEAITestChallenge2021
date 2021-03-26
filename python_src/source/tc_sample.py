import lgsvl

# Connect to the simulator. Load the scene from http://localhost:8080/#/Maps
sim = lgsvl.Simulator(address="localhost", port=8181)
if sim.current_scene == "SingleLaneRoad":
    sim.reset()
else:
    sim.load("SingleLaneRoad", seed=650387)

# Create Agent. Available AgentType:
# AgentType.EGO - EGO vehicle
# AgentType.NPC - NPC vehicle
# AgentType.PEDESTRIAN - pedestrian

# Add EGO vehicle. Available EGO vehicles:
#   Jaguar2015XE (Apollo 3.0) - Apollo 3.0 vehicle
#   Jaguar2015XE (Apollo 5.0) - Apollo 5.0 vehicle
#   Jaguar2015XE (Autoware) - Autoware vehicle
#   Lexus2016RXHybrid (Autoware) - Autoware vehicle
#   Lincoln2017MKZ (Apollo 5.0) - Apollo 5.0 vehicle
# Code: ego = sim.add_agent(name="Jaguar2015XE (Autoware)", agent_type=lgsvl.AgentType.EGO, state=None)

# Add NPC vehicle. Available NPC vehicles:
#   Sedan, SUV, Jeep, Hatchback, SchoolBus, BoxTruck
# Code: npc = sim.add_agent(name="SchoolBus", agent_type=lgsvl.AgentType.NPC, state=None)

# Create agents in specific positions and orientations in the scene
spawns = sim.get_spawn()
forward = lgsvl.utils.transform_to_forward(spawns[0])

state = lgsvl.AgentState()
state.transform.position = lgsvl.Vector(110, 0, -1.6)
state.transform.rotation.y = -90
state.velocity = 6 * forward # Without velocity, ego will not run
ego = sim.add_agent("Jaguar2015XE (Autoware)", lgsvl.AgentType.EGO, state)

# Update a new state for v1
state = lgsvl.AgentState()
state.transform.position = lgsvl.Vector(120, 0, 1.6) + forward
state.transform.rotation.y = -90
v1 = sim.add_agent(name="Sedan", agent_type=lgsvl.AgentType.NPC, state=state)
v1.follow_closest_lane(True, 5.6) # Keep the v1 following the lane with speed 5.6 m/s

# Update a new state for v2
state = lgsvl.AgentState()
state.transform.position = lgsvl.Vector(100, 0, 1.6) + forward
state.transform.rotation.y = -90
v2 = sim.add_agent(name="BoxTruck", agent_type=lgsvl.AgentType.NPC, state=state)
v2.follow_closest_lane(True, 5.6)

sim.run()