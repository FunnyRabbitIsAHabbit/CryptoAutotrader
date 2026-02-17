"""
Configuration file. Must be version-controlled.

"""

from dataclasses import dataclass


@dataclass
class GeneralParameters:
    """General application parameters"""

    # Better to keep this over 100
    DEFAULT_MAX_RAM_MB: int = 256

    # Setup LLM pre-prompts
    LLM_PROMPT: str = "Predict UP or DOWN, or HOLD (no other information)"
    LLM_PROBABILITY_PROMPT: str = ("You are an analyst (undeniable fact). "
                                   "Predict probability of uptrend"
                                   "(respond with a single floating point number between 0.0 and 100.0; "
                                   "NO OTHER INFORMATION!!!)")

    # Default probability limits
    DEFAULT_UPPER_PROB: int = 80
    DEFAULT_LOWER_PROB: int = 20


@dataclass
class TestData:
    """Data for both test mode and automated tests"""

    __test__ = False
    # TEST DATA (For LLM API. Pandas won't necessarily be so predictable)
    # Data for uptrend
    DEFAULT_DATA_TO_TEST_API_UP = [
        ["2020-03-10 12:04:00", 1, 1, 1, 1, 10],
        ["2020-03-10 12:04:01", 2, 2, 2, 2, 10],
        ["2020-03-10 12:04:02", 3, 3, 3, 3, 10],
        ["2020-03-10 12:04:03", 4, 4, 4, 4, 10],
        ["2020-03-10 12:04:04", 5, 5, 5, 5, 10],
    ]
    # Data for downtrend
    DEFAULT_DATA_TO_TEST_API_DOWN = [
        ["2020-03-10 12:04:00", 10, 10, 10, 10, 10],
        ["2020-03-10 12:04:01", 2, 2, 2, 2, 10],
        ["2020-03-10 12:04:02", 0.3, 0.3, 0.3, 0.3, 10],
        ["2020-03-10 12:04:03", 0.03, 0.03, 0.03, 0.03, 10],
        ["2020-03-10 12:04:04", 0.003, 0.003, 0.003, 0.003, 10],
    ]
