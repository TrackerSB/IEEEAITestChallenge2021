from enum import Enum, unique


@unique
class MapModel(Enum):
    BorregasAve = ("BorregasAve", "Borregas Ave", "borregasave.xodr")
    CubeTown = ("CubeTown", "Cubetown", "cubetown.xodr")
    # AutonomouStuff = ("AutonomouStuff", "Autonomous Stuff", "autonomoustuff.xodr")
    SanFrancisco = ("SanFrancisco", "San Francisco", "sanfrancisco.xodr")
    Shalun = ("Shalun", "Shalun", "shalun.xodr")
    Gomentum = ("Gomentum", "Gomentum", "gomentum.xodr")