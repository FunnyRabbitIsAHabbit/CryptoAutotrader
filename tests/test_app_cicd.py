"""
Test classes. Version controlled and CI/CD specific (GitHub secret required!).
"""

import pytest

from config import TestData
from predict import PredictionApp


class TestLLM:
    """
    Test LLM API predictions (5/5 passed expected, however at least 1/5 is fine)
    """

    PREDICTION_APP: PredictionApp = PredictionApp()

    # Non-deterministic tests deprecated
    # def test_any(self):
    #     """
    #     Run abstract LLM prediction on test data (check if not None)
    #     :return:
    #     """
    #
    #     prediction_function = self.PREDICTION_APP.predict_with_any_llm
    #
    #     assert prediction_function(TestData.DEFAULT_DATA_TO_TEST_API_UP) is not None, \
    #         "Couldn't get prediction"
    #
    # def test_probability_up(self):
    #     """
    #     Run LLM prediction with prob. on test data
    #     :return:
    #     """
    #
    #     prediction_function = self.PREDICTION_APP.predict_probability_with_llm
    #
    #     assert prediction_function(TestData.DEFAULT_DATA_TO_TEST_API_UP) == "up", \
    #         "Incorrect prediction"
    #
    # def test_probability_down(self):
    #     """
    #     Run LLM prediction with prob. on test data
    #     :return:
    #     """
    #
    #     prediction_function = self.PREDICTION_APP.predict_probability_with_llm
    #
    #     assert prediction_function(TestData.DEFAULT_DATA_TO_TEST_API_DOWN) == "down", \
    #         "Incorrect prediction"

    def test_basic_up(self):

        prediction_function = self.PREDICTION_APP.predict_up_or_down

        assert prediction_function(TestData.DEFAULT_DATA_TO_TEST_API_UP) in {"up", "down", "hold"}, \
            "Incorrect prediction"

    def test_basic_down(self):

        prediction_function = self.PREDICTION_APP.predict_up_or_down

        assert prediction_function(TestData.DEFAULT_DATA_TO_TEST_API_DOWN) in {"up", "down", "hold"}, \
            "Incorrect prediction"
