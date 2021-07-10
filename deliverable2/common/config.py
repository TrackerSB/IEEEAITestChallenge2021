from enum import auto, Enum, unique


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


@unique
class SupportedMap(Enum):
    BorregasAve = ("BorregasAve", "Borregas Ave")
    CubeTown = ("CubeTown", "Cubetown")
    SanFrancisco = auto()
    Shalun = auto()


@unique
class SupportedNPC(AutoName):
    BoxTruck = auto()
    Hatchback = auto()
    Jeep = auto()
    SchoolBus = auto()
    Sedan = auto()
    SUV = auto()


# The list of available pedestrians can be found in the maps PedestrianManager prefab
# NOTE The availability of pedestrian names may depend on the currently used map
@unique
class SupportedPedestrian(AutoName):
    Bob = auto()
    EntrepreneurFemale = auto()
    Howard = auto()
    Johny = auto()
    Pamela = auto()
    Presley = auto()
    Robin = auto()
    Stephen = auto()
    Zoe = auto()


@unique
class SupportedDreamViewCar(Enum):
    Lincoln2017MKZ = "2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921"
    Jaguar2015XE = "09510748-1f41-484e-9495-7d17129a62e3"


class ApolloModule(AutoName):
    Camera = auto()
    Control = auto()
    Localization = auto()
    Perception = auto()
    Planning = auto()
    Prediction = auto()
    Routing = auto()
    TrafficLight = auto()
    Transform = auto()
