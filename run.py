"""
Main bot module

@Developer: Stan
@AppVersion: 3.3.1
@PythonVersion: 3.13

"""

# Python default library ---------
import argparse
import sys
from os import PathLike
from os.path import abspath, dirname, join
from typing import Any, Callable
# --------------------------------

# Own modules --------------------
import dashboard
from config import TestData
from integrate_dashboard import OutputIntegration
from predict import PredictionApp
from trading_bot import TradingBot
# --------------------------------


def global_main() -> None:
    """
    Function to call for main run logic

    :return: None
    """

    console_arguments_parser = argparse.ArgumentParser(
        prog="run.py",
        description="run.py will place trades in accordance with specified parameters. "
                    "Use with `test` command to only run default data through prediction API; "
                    "use with `run` command to run main functionality.",
        epilog="Extremely caution is advised, don't run the program unless knowing EXACTLY what will happen."
    )
    default_main_environment_filename = "main.env"
    default_prediction_environment_filename = "probability_llm.env"
    subparsers = console_arguments_parser.add_subparsers(
        dest="running_mode",
        required=True
    )
    parser_test_predict_api = subparsers.add_parser("test")
    parser_test_predict_api.add_argument(
        "-p", "--predictions",
        default=default_prediction_environment_filename,
        type=str,
        required=False,
    )
    parser_run = subparsers.add_parser("run")
    parser_run.add_argument(
        "-e", "--env",
        default=default_main_environment_filename,
        type=str,
        required=False,
    )
    parser_run.add_argument(
        "-p", "--predictions",
        default=default_prediction_environment_filename,
        type=str,
        required=False,
    )
    # New argument for dashboard mode:
    parser_run.add_argument(
        "-d", "--dashboard",
        action="store_true",
        help="Launch the app in dashboard mode (powered by Streamlit)"
    )

    console = console_arguments_parser.parse_args()
    mode = console.running_mode

    # Paths
    current_path: str | PathLike = dirname(abspath(__file__))
    predictions_env_path: str | PathLike = join(current_path, console.predictions)

    # Predictions
    prediction_app: PredictionApp = PredictionApp(env_file_path=predictions_env_path)
    prediction_function: Callable[[Any], str] = prediction_app.predict_up_or_down

    match mode:
        case "run":
            main_trading_env_path = join(current_path, console.env)

            # If -d or --dashboard flags have been used to run the script
            if console.dashboard:
                print("[START]\tRunning in `run` mode with dashboard & trading logic concurrently.")
                trading_bot: TradingBot = TradingBot(
                    prediction_api=prediction_function,
                    output_integration=OutputIntegration("dashboard"),
                    env_file_path = main_trading_env_path
                )
                dashboard.run_dashboard()

            # No -d or --dashboard flag has been given
            else:
                print("[START]\tStarted module in `run` mode without dashboard.")
                trading_bot: TradingBot = TradingBot(
                    prediction_api=prediction_function,
                    output_integration=OutputIntegration("console"),
                    env_file_path=main_trading_env_path
                )

            # Regardless of usage of -d or --dashboard flags
            sys.exit(trading_bot.main(infinite_loop_condition=True))

        case "test":
            print("[START]\tSTARTED module in `test` mode.")
            print("\t[INFO]\tUptrend recognized ?",
                  prediction_function(TestData.DEFAULT_DATA_TO_TEST_API_UP))
            print("\t[INFO]\tDowntrend recognized ?",
                  prediction_function(TestData.DEFAULT_DATA_TO_TEST_API_DOWN))
            sys.exit(print("END] Test mode exited."))



if __name__ == "__main__":
    global_main()
