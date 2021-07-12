from .map import MapModel


class Scenario:
    def __init__(self, start, end, mmap: MapModel, tc_id: int, park=None):
        self.start = start
        self.end = end
        self.map = mmap
        self.ID = str(tc_id)
        self.park = park

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)