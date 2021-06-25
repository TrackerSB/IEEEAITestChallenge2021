from tkinter import Canvas
from typing import Set, List, Tuple, Dict

from opendrive2lanelet.opendriveparser.elements.junction import Junction
from opendrive2lanelet.opendriveparser.elements.road import Road
from shapely.geometry import Point, Polygon


def _create_empty_plot(width: float = 500, height: float = 500) -> Canvas:
    from tkinter import Tk
    master = Tk()
    master.title = "Road network"
    master.configure(background="black")
    canvas = Canvas(master, width=width, height=height)
    canvas.configure(background="white")
    canvas.pack()
    return canvas


def _interpolate_roads(roads: Set[Road]) -> Tuple[Dict[int, List[Point]], Polygon]:
    from math import floor
    from shapely.geometry import box
    resolution: int = 10  # Steps per meter for visualizing roads
    road_points_collection: Dict[int, List[Point]] = {}
    min_x: float = float("Infinity")
    max_x: float = float("-Infinity")
    min_y: float = float("Infinity")
    max_y: float = float("-Infinity")
    for road in roads:
        plan_view = road.planView
        road_points: List[Point] = []
        for i in range(0, floor(plan_view.length * resolution)):
            current_point = Point(plan_view.calc(i / resolution)[0])
            min_x = min(current_point.x, min_x)
            max_x = max(current_point.x, max_x)
            min_y = min(current_point.y, min_y)
            max_y = max(current_point.y, max_y)
            road_points.append(current_point)
        road_points.append(Point(plan_view.calc(plan_view.length)[0]))  # Ensure end points of roads are included
        road_points_collection[road.id] = road_points
    return road_points_collection, box(min_x, min_y, max_x, max_y)


def _shift_points(points: List[Point], shift_x: float, shift_y: float) -> List[Point]:
    return [Point(p.x+shift_x, p.y+shift_y) for p in points]


def _add_road_plot(canvas: Canvas, road: List[Point], color: str = "black") -> None:
    from typing import Optional
    last_position: Optional[Point] = None
    for point in road:
        next_position = point
        if last_position is not None:
            canvas.create_line(last_position.x, last_position.y, next_position.x, next_position.y, fill=color)
        last_position = next_position


def _add_junction_plots(canvas: Canvas, roads: Dict[int, List[Point]], junctions: List[Junction]) -> None:
    for junction in junctions:
        for connection in junction.connections:
            incoming_road_id = connection.incomingRoad
            connecting_road = connection.connectingRoad
            _add_road_plot(canvas, roads[incoming_road_id], "black")
            _add_road_plot(canvas, roads[connecting_road], "red")


def _main() -> None:
    from common.open_drive_reader import get_roads_and_junctions
    from tkinter import mainloop

    roads, junctions = get_roads_and_junctions("autonomoustuff.xodr")
    road_points, bounding_box = _interpolate_roads(roads)

    required_width = bounding_box.bounds[2] - bounding_box.bounds[0]
    required_height = bounding_box.bounds[3] - bounding_box.bounds[1]
    required_x_shift = -bounding_box.bounds[0]
    required_y_shift = -bounding_box.bounds[1]
    shifted_road_points = {}
    for rid, road in road_points.items():
        shifted_road_points[rid] = _shift_points(road, required_x_shift, required_y_shift)

    canvas = _create_empty_plot(required_width, required_height)
    _add_junction_plots(canvas, shifted_road_points, junctions)

    mainloop()


if __name__ == "__main__":
    _main()
