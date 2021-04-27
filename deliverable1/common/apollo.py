from enum import Enum

from lgsvl import EgoVehicle, Vector
from lgsvl.dreamview import Connection


class ApolloModule(Enum):
    Camera = "Camera"
    Control = "Control"
    Localization = "Localization"
    Perception = "Perception"
    Planning = "Planning"
    Prediction = "Prediction"
    Routing = "Routing"
    TrafficLight = "TrafficLight"
    Transform = "Transform"


_INITIAL_MODULES = [
    ApolloModule.Localization,
    ApolloModule.Perception,
    ApolloModule.Planning,
    ApolloModule.Transform,
    ApolloModule.Routing,
    ApolloModule.Prediction
]


def _connect_to_apollo(ego: EgoVehicle, host: str, port: int, timeout_secs: int) -> None:
    from time import sleep
    ego.connect_bridge(host, port)
    seconds_waited = 0
    while not ego.bridge_connected:
        print("Wait for Apollos bridge to connect...")
        sleep(1)
        seconds_waited += 1
        if seconds_waited > timeout_secs:
            raise ConnectionRefusedError("Connecting to Apollos bridge timed out")


def _enable_modules(dv_connection: Connection, *modules: ApolloModule) -> None:
    for module in modules:
        dv_connection.enable_module(module.value)


def connect_to_dreamview(ego: EgoVehicle, destination: Vector, apollo_host: str, apollo_port: int, dreamview_port: int,
                         timeout_secs: int = 20) -> Connection:
    _connect_to_apollo(ego, apollo_host, apollo_port, timeout_secs)
    dv_connection = Connection(ego.simulator, ego, port=str(dreamview_port))
    dv_connection.disable_apollo()  # Ensure restart of Apollo modules
    dv_connection.enable_apollo(destination.x, destination.z, [m.name for m in _INITIAL_MODULES])
    return dv_connection
