from lgsvl import Vector


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
