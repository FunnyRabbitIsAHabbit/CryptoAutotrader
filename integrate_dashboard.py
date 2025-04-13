from typing import Literal, Self

from dashboard import add_info_message, add_memory_messages, add_transaction_cost


class OutputIntegration:
    """Class to connect messages logic to other modules"""

    def __init__(self: Self, mode: Literal["dashboard", "console"]):
        self.mode = mode

    @property
    def output(self: Self):
        """How to process a general info message

        :return: Callable object
        """

        # Just printing the message out
        if self.mode == "console":
            return print

        # Running the message through another function
        elif self.mode == "dashboard":
            return add_info_message

    @property
    def handle_data(self: Self):
        """How to process deal value (cost of transaction)

        :return: Callable object
        """

        # Doing nothing when data is received by this function
        if self.mode == "console":
            return lambda *args, **kwargs: None

        # Running data through external function
        elif self.mode == "dashboard":
            return add_transaction_cost

    @property
    def handle_memory_data(self: Self):
        """How to process a memory message

        :return: Callable object
        """

        # Just printing the message out
        if self.mode == "console":
            return print

        # Running the message through another function
        elif self.mode == "dashboard":
            return add_memory_messages
