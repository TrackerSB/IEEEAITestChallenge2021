from enum import Enum, unique


@unique
class SupportedMap(Enum):
    BorregasAve = ("BorregasAve", "Borregas Ave", "borregasave.xodr")
    CubeTown = ("CubeTown", "Cubetown", "cubetown.xodr")
    AutonomouStuff = ("AutonomouStuff", "Autonomous Stuff", "autonomoustuff.xodr")