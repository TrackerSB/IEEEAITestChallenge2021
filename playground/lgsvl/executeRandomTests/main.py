from queue import Queue

from lgsvl import Simulator
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

sim = None
roads = None
road_points = None
junctions = None
allowed_area = None
entry_segment = None
final_segment = None
ego = None


def calc_allowed_area():
    global road_points, entry_segment, final_segment, junctions
    r = []
    q = Queue()
    q.put([entry_segment])
    while not q.empty():
        s = q.get()
        succ = s[-1].link.successor
        if succ is None:
            continue
        if succ.elementType == "junction":
            for j in junctions:
                if j.id != succ.element_id:
                    continue
                for c in j.connections:
                    if c.incomingRoad != s[-1].id:
                        continue
                    aj = True
                    sext = s.copy()
                    sext.append(road_points[c.connectingRoad])
                    q.put(sext)
        elif succ.elementType == "road":
            su = road_points[succ.element_id]
            sext = s.copy()
            sext.append(su)
            if su.id == final_segment.id:
                r.append(sext)
            elif len(sext) <= 123:
                q.put(sext)

    a = []
    for rs in r:
        ps = []
        for s in rs:
            ps.extend([(p.x, p.y) for p in s.interpolated_points])
        ls = LineString(ps)
        a.append(ls.buffer(5))

    return unary_union(a)


def test_oracle():
    global ego, allowed_area
    return allowed_area.contains(Point(ego.state.position.x, ego.state.position.z))


def _execute_test(connection) -> None:
    from common.apollo import connect_to_dreamview
    from common.config import SupportedDreamViewCar, SupportedMap, ApolloModule
    from common.scene import generate_initial_state, get_entry_final_point, load_ego, load_scene
    global sim, roads, junctions, road_points, allowed_area, entry_segment, final_segment, ego
    load_scene(sim, SupportedMap.BorregasAve)
    entry_segment, entry_estimation, final_segment, final_estimation = get_entry_final_point(roads, connection, 20)
    allowed_area = calc_allowed_area()
    initial_state = generate_initial_state(entry_estimation)
    ego = load_ego(sim, SupportedDreamViewCar.Lincoln2017MKZ, initial_state)

    # Connect DreamView
    dreamview = connect_to_dreamview(ego, final_estimation.position, "127.0.0.1", 9090, 8888)
    dreamview.set_hd_map("Borregas Ave")
    dreamview.enable_module(ApolloModule.Control.value)

    timeout = 10
    passed = 0
    while passed < timeout:
        sim.run(1)
        if not test_oracle():
            print("test failed")
            return
        passed = passed + 1

    print("test passed")


def _main() -> None:
    from common.geometry import interpolate_roads
    from common.open_drive_reader import get_roads_and_junctions
    global sim, roads, junctions, road_points

    # Parse map roads and junctions
    roads, junctions = get_roads_and_junctions("borregasave.xodr")
    road_points, _ = interpolate_roads(roads)

    # Setup simulation
    sim = Simulator()

    # Find random position on any junction
    for junction in junctions:
        for connection in junction.connections:
            _execute_test(connection)


if __name__ == "__main__":
    _main()
