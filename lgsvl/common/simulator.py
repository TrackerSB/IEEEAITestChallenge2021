from lgsvl import Simulator


def connect_simulation(host: str, port: int) -> Simulator:
    from lgsvl.simulator import env
    return Simulator(env.str("LGSVL__SIMULATOR_HOST", host),
                     env.int("LGSVL__SIMULATOR_PORT", port))
