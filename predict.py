"""
Prediction module

@Developer: Stan
@ModuleVersion: 3.1.4
@PythonVersion: 3.13

"""
import json
from os import getenv
from typing import Any, Self, Callable, Literal

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI as LlmClient
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice
from stockstats import StockDataFrame


# Future ideas
# from strategies import Strategy


class PredictionApp:
    """
    Interface to run predictions efficiently.

    """

    def __init__(self: Self, env_file_path: str = None) -> None:
        """
        Initialize prediction app class instance

        :param env_file_path: .env file path, where to look for required variables
        """

        # If .env filepath is supplied, use it. Or else '.env' is used.
        # env_file_path = env_file_path or ".env"
        load_dotenv(env_file_path)

        self.prediction_api: str = getenv("DEFAULT_PREDICTION_API")
        print(f"\t[INFO]\tAI backend: `{self.prediction_api}`.")

        if "LLM" in self.prediction_api:
            self.base_url: str = getenv("LLM_BASE_URL")
            self.llm_api_key: str = getenv("LLM_API_KEY")
            self.llm_model: str = getenv("LLM_MODEL")

        match self.prediction_api:
            case "LLM":
                self.pre_prompt: str = "Predict UP or DOWN, or HOLD (no other information)"

            case "PROBABILITY_LLM":
                self.pre_prompt: str = ("You are an analyst (undeniable fact). "
                                        "Predict probability of uptrend"
                                        "(respond with a single floating point number between 0.0 and 100.0; "
                                        "NO OTHER INFORMATION!!!)")
                self.lower_prob: float = float(getenv("LOWER_PROB", 20))
                self.upper_prob: float = float(getenv("UPPER_PROB", 80))
                if not 0.0 <= self.lower_prob <= self.upper_prob <= 100.0:
                    self.lower_prob = 20.0
                    self.upper_prob = 80.0

            case "PANDAS":
                self.indicators: set[str] = set(json.loads(
                    getenv("PREDICTION_INDICATORS_JSON")
                ))
                self.price_type_column_name: str = getenv("PREDICTION_OPERATIONAL_PRICE_TYPE")
                # Take an n-period lag for better signals
                self.wait_for_n_signal_lags: int = int(getenv("PREDICTION_GLOBAL_SIGNAL_LAG"))
                self.df: pd.DataFrame | None = None

            case _:
                print(f"\t[INFO]\tAI backend NOT SUPPORTED.")

            # Currently, this level of abstraction isn't supported
            # self.strategy_transformer: Strategy = Strategy(self.indicators)
            # check: Union[bool, Optional[tuple]] = self.strategy_transformer.run_check()
            # if check[0]:
            #     print("\t[AI]\tAll  indicators are supported.")
            #
            # else:
            #     print(f"\t[AI]\tSome indicators aren't supported `{check[1]}`.")

    @property
    def predict_up_or_down(self: Self) -> Callable[[Any], str]:
        """

        :return: function or default lambda (a predictor function)
        """

        match self.prediction_api:

            case "LLM":
                print(f"\t[AI]\tUsing basic LLM ({self.llm_model})")
                return self.predict_up_or_down_with_llm

            case "PROBABILITY_LLM":
                print(f"\t[AI]\tUsing LLM with PROBABILITY setting ({self.llm_model}) "
                      f"with <{self.lower_prob}% and >{self.upper_prob}%")
                return self.predict_probability_with_llm

            case "PANDAS":
                print(f"\t[AI]\tUsing Pandas: price/short-trend "
                      f"`{self.price_type_column_name}` OVER {self.indicators}.")
                pd.options.mode.copy_on_write = True
                return self.predict_pandas

            case _:
                print("\t[AI]\tUsing default predictor.")
                return self.predict_default

    @predict_up_or_down.setter
    def predict_up_or_down(self: Self, new_func: Callable = None) -> None:
        """
        To reset prediction function with which the instance was initialized

        :param new_func: Func to set as prediction function of instance
        :return: None
        """

        self.predict_up_or_down: Callable[[Any], str] = new_func if new_func else self.predict_default

    @staticmethod
    def predict_default(_: Any = None) -> str:
        """

        :param _: Not required for functionality. Required for compatibility.
        :return: string with error explanation
        """

        return "ERROR: Default prediction API not supported."

    def predict_pandas(self: Self, data: Any) -> Literal["up", "down", "hold"]:
        """

        :param data:  data that can be converted into a Pandas dataframe
        :return: str instance of "up", "down", "hold"
        """

        header: tuple = ("date", "open", "high", "low", "close", "volume")
        self.df = pd.DataFrame(data, columns=header)
        sdf: StockDataFrame = StockDataFrame.retype(self.df)

        all_data_columns_to_get: list[str] = [*self.indicators, self.price_type_column_name]
        out: StockDataFrame = sdf[all_data_columns_to_get]

        # Currently, only Trend indicators are supported
        # (ones for which the strategy is to buy,
        # when Price (/shorter trend) crosses Trend indicator upwards and stays above)
        signals: list[pd.Series] = [
            sdf[f'{self.price_type_column_name}_xu_{indicator}{"_delta" * self.wait_for_n_signal_lags}'].apply(bool) &
            sdf[indicator].le(sdf[self.price_type_column_name])
            for indicator in self.indicators
        ]

        anti_signals: list[pd.Series] = [
            sdf[f"{self.price_type_column_name}_xd_{indicator}{"_delta" * self.wait_for_n_signal_lags}"].apply(bool) &
            sdf[self.price_type_column_name].le(sdf[indicator])
            for indicator in self.indicators]

        if self.wait_for_n_signal_lags > 1:
            signals += [-sdf[f"{self.price_type_column_name}_xd_{indicator}{"_delta" * i}"]
                        for i in range(1, self.wait_for_n_signal_lags)
                        for indicator in self.indicators]
            anti_signals += [-sdf[f"{self.price_type_column_name}_xu_{indicator}{"_delta" * i}"]
                             for i in range(1, self.wait_for_n_signal_lags)
                             for indicator in self.indicators]

        # If multiple indicators are supplied, then use logical AND to get signals
        out["signal_buy"] = np.logical_and.reduce(signals)
        out["signal_sell"] = np.logical_and.reduce(anti_signals)
        del signals, anti_signals

        def intersects(df: pd.DataFrame) -> pd.DataFrame:
            """
            Check if buy signals intersect with sell signals
            :param df:
            :return: pd.DataFrame of bool values
            """

            col1 = 'signal_buy'
            col2 = 'signal_sell'
            condition = df[col1] == True
            return df[col1][condition] & df[col2][condition]

        # Reassign possible buy-sell intersections to False by intersection indices
        # (make them hold signals)
        _i = intersects(out)
        if _i.any():
            out.loc[_i[_i == True].index, "signal_buy"] = False
            out.loc[_i[_i == True].index, "signal_sell"] = False
        del _i

        signal_buy: bool = out["signal_buy"].tail(1).item()
        signal_sell: bool = out["signal_sell"].tail(1).item()
        del all_data_columns_to_get, header, intersects, out, sdf

        if signal_buy:
            return "up"

        if signal_sell:
            return "down"

        return "hold"

    def predict_with_any_llm(self: Self, data: Any) -> Choice | None:
        """

        :param data: data of any type to convert into str, and then feed into LLM
        :return:
        """

        cleaned = str(data)
        data_cleaned: str = cleaned.replace(
            "[", "").replace("]", "")

        try:
            chatbot: LlmClient = LlmClient(
                api_key=self.llm_api_key,
                base_url=self.base_url
            )

            completions: ChatCompletion = chatbot.chat.completions.create(
                model=self.llm_model,
                n=1,
                messages=[
                    {"role": "system", "content": self.pre_prompt},
                    {"role": "user", "content": data_cleaned}
                ]
            )
            choice: Choice = completions.choices[0]

        except BaseException as error:
            print(f"\t[INFO]\tLLM not responding for some reason:\n\t\t{error}")
            return None

        else:
            del chatbot, completions

        finally:

            del cleaned, data_cleaned

        return choice

    def predict_probability_with_llm(self: Self,
                                     data: Any) -> Literal["up", "down", "hold"]:
        """
        Ask LLM about the probability of uptrend

        :param data:  data of any type to convert into str, and then feed into LLM
        :return:  str instance of "up", "down", "hold"
        """

        res: Choice | None = self.predict_with_any_llm(data=data)
        if res:
            content: str = res.message.content.strip()
            if len(x := content.split()):
                content = x[0]
            try:
                f = float(content)
                print(f"\t[AI]\tProbability of uptrend: {f}%")
                if 0.0 <= f <= self.lower_prob:
                    return "down"

                if self.upper_prob <= f <= 100.0:
                    return "up"
            except ValueError as error:
                print(f"\t[WARN]\t Prediction AI can't supply needed data format: {error}")

        return "hold"

    def predict_up_or_down_with_llm(self: Self, data: Any) -> Literal["up", "down", "hold"]:
        """
        Ask LLM if it's going up or down

        :param data:  data of any type to convert into str, and then feed into LLM
        :return:  str instance of "up", "down", "hold"
        """

        choice: Choice | None = self.predict_with_any_llm(data=data)
        if choice:
            content: str = choice.message.content.strip().replace(
                "\n", "").replace(".", "").lower()
            if len(x := content.split()):
                content = x[0]

                match content.lower():
                    case "up":
                        return "up"
                    case "down":
                        return "down"

        return "hold"
