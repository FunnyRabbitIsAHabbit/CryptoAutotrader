"""
Configuration file. Must be version-controlled.

"""

from dataclasses import dataclass


@dataclass
class GeneralParameters:
    """General application parameters"""

    # Better to keep this over 100
    DEFAULT_MAX_RAM_MB: int = 256


@dataclass
class Color:
    """USAGE DEPRECATED. Colors to alter console output"""

    PURPLE: str = "\033[95m"
    CYAN: str = "\033[96m"
    DARK_CYAN: str = "\033[36m"
    BLUE: str = "\033[94m"
    GREEN: str = "\033[92m"
    YELLOW: str = "\033[93m"
    RED: str = "\033[91m"
    BOLD: str = "\033[1m"
    ITALIC: str = "\x1B[3m"
    UNDERLINE: str = "\033[4m"
    END: str = "\033[0m"

@dataclass
class DashServer:
    """Dashboard server settings"""

    HOST: str = "0.0.0.0"
    PORT: int = 8050


class Styles:
    """CCS styles for Dashboard"""

    GENERIC_DIV: dict = {
        "backgroundColor": "rgba(0,0,0,0.6)",  # Dark background for containers
        "padding": "20px",
        "borderRadius": "15px",
        "marginBottom": "20px",
        "boxShadow": "0px 4px 10px rgba(0, 0, 0, 0.4)"
    }
    GENERIC_FONT: dict = {"color": "#F4F1EB", "fontFamily": "Poppins, sans-serif"}
    HEADER: dict = {
        "textAlign": "center",
        "fontFamily": "Poppins, sans-serif",
        "color": "#F4F1EB",  # Eggshell white color for contrast
        "backgroundColor": "rgba(0,0,0,0.7)",  # Dark background for the header
        "padding": "30px",
        "borderRadius": "15px",
        "boxShadow": "0px 4px 10px rgba(0, 0, 0, 0.5)"
    }
    INTERVAL: dict = {
        "background": "linear-gradient(135deg, #E6AA68, #E04E1F, #00B1D2)",
        # New vibrant gradient with Pantone 15-0948 Golden Glow, 17-1446 Tangerine Tango, 16-4535 Blue Atoll
        "color": "#F4F1EB",  # Eggshell white color for text
        "fontFamily": "Poppins, sans-serif",
        "padding": "40px",
        "borderRadius": "15px",
        "boxShadow": "0px 4px 15px rgba(0, 0, 0, 0.2)"
    }
    PARAGRAPH: dict = {
        "fontSize": "20px",
        "color": "#F4F1EB",
        "fontFamily": "Poppins, sans-serif"
    }
    UNORDERED_LIST: dict = GENERIC_FONT | {"list-style": "none",
                                           "text-wrap": "wrap",
                                           "line-height": "1.5"}


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
