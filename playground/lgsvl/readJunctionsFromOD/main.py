from tkinter import Canvas
from typing import Set

from opendrive2lanelet.opendriveparser.elements.road import Road


def _create_empty_plot(width: float = 500, height: float = 500) -> Canvas:
    from tkinter import Tk
    master = Tk()
    master.title = "Road network"
    master.configure(background="black")
    canvas = Canvas(master, width=width, height=height)
    canvas.configure(background="white")
    canvas.pack()
    return canvas


def _add_road_plots(canvas: Canvas, roads: Set[Road]) -> None:
    from math import floor
    from typing import Optional, Tuple
    resolution: int = 10
    for road in roads:
        plan_view = road.planView
        last_position: Optional[Tuple[float, float]] = None
        for i in range(0, floor(plan_view.length * resolution)):
            next_position = plan_view.calc(i/resolution)[0]
            print("f({}) == {}".format(i, next_position))
            if last_position is not None:
                canvas.create_line(last_position[0]+200, last_position[1]+200, next_position[0]+200, next_position[1]+200)
            last_position = next_position


def _main() -> None:
    from common.open_drive_reader import get_roads_and_junctions
    from tkinter import mainloop

    roads, junctions = get_roads_and_junctions("autonomoustuff.xodr")
    canvas = _create_empty_plot()  # FIXME Adapt size to road network
    _add_road_plots(canvas, roads)

    mainloop()


if __name__ == "__main__":
    _main()
