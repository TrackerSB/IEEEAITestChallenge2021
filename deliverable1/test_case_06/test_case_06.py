import unittest
from sys import stdout
from typing import Callable

from .locations import ALL_LOCATIONS, Location
from .config import TestConfig
from .executor import TestCase6

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


class TestCase06(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import logging.config
        logging.config.dictConfig(LOGGING_CONFIG)

    def _iterate_configs(self, config_provider: Callable[[Location, bool], TestConfig]) -> None:
        import logging

        all_succeeded = True
        for location in ALL_LOCATIONS:
            for pedestrian_direction in [True, False]:
                config = config_provider(location, pedestrian_direction)
                from common import SimConnection
                with SimConnection(load_scene=False) as sim:
                    test_result = TestCase6.execute(sim, config)
                    if test_result is None:
                        logging.warning("Skipped config {}".format(config))
                    else:
                        if not test_result:
                            logging.debug("Failed with config {}".format(config))
                            all_succeeded = False
        self.assertTrue(all_succeeded,
                        "The ego vehicle failed with the previously given configurations (See logging output)")

    def test_enforceCrashSlow(self) -> None:
        from .config import TestConfig

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
        from .config import TestConfig

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
        from .config import TestConfig

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
        from .config import TestConfig

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
        from .config import TestConfig

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
        from .config import TestConfig

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
