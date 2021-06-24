from typing import Set, Tuple, Dict, List

from lgsvl import Vector
from opendrive2lanelet.opendriveparser.elements.road import Road
from shapely.geometry import Point, Polygon


def _dot_product(a: Vector, b: Vector) -> float:
    return a.x * b.x + a.y * b.y + a.z * b.z


def _cross_product(a: Vector, b: Vector) -> Vector:
    return Vector(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * a.x
    )


def get_directional_angle(a: Vector, b: Vector) -> float:
    """
    :param a: A vector in the XZ plane
    :param b: Another vector in the XZ plane
    :return: The clockwise angle between a and b on the XZ plane in degrees
    """
    from math import atan2, degrees
    cross_ab = _cross_product(a, b)
    dot_ab = _dot_product(a, b)
    return -degrees(atan2(_dot_product(cross_ab, Vector(0, 1, 0)), dot_ab))


def rotate_around_y(a: Vector, angle: float) -> Vector:
    """
    :param angle: Clockwise angle in degrees
    """
    from math import cos, sin, radians
    acw_angle = -radians(angle)
    return Vector(
        a.x * cos(acw_angle) + a.z * sin(acw_angle),
        a.y,
        -a.x * sin(acw_angle) + a.z * cos(acw_angle)
    )


def interpolate_roads(roads: Set[Road]) -> Tuple[Dict[int, List[Point]], Polygon]:
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
