class Scenario:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)