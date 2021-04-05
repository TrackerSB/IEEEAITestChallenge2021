import unittest
from sys import stdout
from typing import Callable

from lgsvl import Simulator

from tc6.config import TestConfig
from tc6.testcase6 import TestCase6
from tc6.locations import ALL_LOCATIONS, Location

LGSVL_HOST: str = "127.0.0.1"
LGSVL_PORT: int = 8181
LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": stdout
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG"
    }
}


class TC6TestSuite(unittest.TestCase):
    _sim: Simulator = None

    @classmethod
    def setUpClass(cls) -> None:
        from common.simulator import connect_simulation
        import logging.config
        TC6TestSuite._sim = connect_simulation(LGSVL_HOST, LGSVL_PORT)
        logging.config.dictConfig(LOGGING_CONFIG)

    @classmethod
    def tearDownClass(cls) -> None:
        TC6TestSuite._sim.stop()

    def _iterate_configs(self, config_provider: Callable[[Location, bool], TestConfig]) -> None:
        import logging
        from inspect import currentframe, getouterframes

        current_frame = currentframe()
        calling_frame = getouterframes(current_frame, 2)
        logging.info("Start {}".format(calling_frame[1][3]))

        all_succeeded = True
        for location in ALL_LOCATIONS:
            for pedestrian_direction in [True, False]:
                config = config_provider(location, pedestrian_direction)
                test_result = TestCase6.execute(TC6TestSuite._sim, config)
                if test_result is None:
                    logging.warning("Skipped config {}".format(config))
                else:
                    if not test_result:
                        logging.debug("Failed with config {}".format(config))
                        all_succeeded = False
        self.assertTrue(all_succeeded,
                        "The ego vehicle failed with the previously given configurations (See logging output)")

    def test_enforceCrashSlow(self) -> None:
        from tc6.config import TestConfig

        def _generate_config(location: Location, pedestrian_direction: bool) -> TestConfig:
            return TestConfig(
                "Jaguar2015XE",
                "Jaguar2015XE (Apollo 5.0, many sensors)",
                30.0,
                None,
                pedestrian_direction,
                location
            )

        self._iterate_configs(_generate_config)

    def test_enforceCrashFast(self) -> None:
        from tc6.config import TestConfig

        def _generate_config(location: Location, pedestrian_direction: bool) -> TestConfig:
            return TestConfig(
                "Jaguar2015XE",
                "Jaguar2015XE (Apollo 5.0, many sensors)",
                60.0,
                None,
                pedestrian_direction,
                location
            )

        self._iterate_configs(_generate_config)

    def test_nearSlow(self) -> None:
        from tc6.config import TestConfig

        def _generate_config(location: Location, pedestrian_direction: bool) -> TestConfig:
            return TestConfig(
                "Jaguar2015XE",
                "Jaguar2015XE (Apollo 5.0, many sensors)",
                30.0,
                40.0,
                pedestrian_direction,
                location
            )

        self._iterate_configs(_generate_config)

    def test_nearFast(self) -> None:
        from tc6.config import TestConfig

        def _generate_config(location: Location, pedestrian_direction: bool) -> TestConfig:
            return TestConfig(
                "Jaguar2015XE",
                "Jaguar2015XE (Apollo 5.0, many sensors)",
                60.0,
                40.0,
                pedestrian_direction,
                location
            )

        self._iterate_configs(_generate_config)

    def test_farSlow(self) -> None:
        from tc6.config import TestConfig

        def _generate_config(location: Location, pedestrian_direction: bool) -> TestConfig:
            return TestConfig(
                "Jaguar2015XE",
                "Jaguar2015XE (Apollo 5.0, many sensors)",
                30.0,
                200.0,
                pedestrian_direction,
                location
            )

        self._iterate_configs(_generate_config)

    def test_farFast(self) -> None:
        from tc6.config import TestConfig

        def _generate_config(location: Location, pedestrian_direction: bool) -> TestConfig:
            return TestConfig(
                "Jaguar2015XE",
                "Jaguar2015XE (Apollo 5.0, many sensors)",
                60.0,
                200.0,
                pedestrian_direction,
                location
            )

        self._iterate_configs(_generate_config)


if __name__ == '__main__':
    unittest.main()
