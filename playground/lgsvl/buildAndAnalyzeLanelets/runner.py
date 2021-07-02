from lanelet import LaneLet, Path
from sim import Sim
from supportedmap import SupportedMap


if __name__ == "__main__":
    for map in [SupportedMap.CubeTown, SupportedMap.BorregasAve, SupportedMap.AutonomouStuff]:
        lanelet = LaneLet(map.value[2])
        path_model = Path(lanelet.intersections, lanelet.lanelet_network)
        for intersection in lanelet.intersections:
            path_model.generate_driving_paths(intersection, map.value[0])

    # Run a simulation
    # Sim.run_simulation(points[0], points[1], map)