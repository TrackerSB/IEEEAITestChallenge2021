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
    from common.geometry import interpolate_roads
    from common.open_drive_reader import get_roads_and_junctions
    from tkinter import mainloop

    roads, junctions = get_roads_and_junctions("autonomoustuff.xodr")
    road_points, bounding_box = interpolate_roads(roads)

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
