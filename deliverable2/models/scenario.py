class Scenario:
    def __init__(self, start, end, mmap, dvmap, tc_id: int, park=None, side=0):
        self.start = start
        self.end = end
        self.map = mmap
        self.ID = str(tc_id)
        self.park = park
        self.dvmap = dvmap
        self.side = side

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)