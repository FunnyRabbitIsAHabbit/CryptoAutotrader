from typing import Literal, Self

from base_output import add_info_message, add_memory_messages, add_transaction_cost


class OutputIntegration:
    """Class to connect messages logic to other modules"""

    def __init__(self: Self, mode: Literal["base", "console"]):
        self.mode = mode

    @property
    def output(self: Self):
        """How to process a general info message

        :return: Callable object
        """

        # Just printing the message out
        match self.mode:
            case "console":
                return print

        # Running the message through another function
            case "base":
                return add_info_message

            case _:

                return None

    @property
    def handle_data(self: Self):
        """How to process deal value (cost of transaction)

        :return: Callable object
        """

        # Doing nothing when data is received by this function
        match self.mode:
            case "console":
                return lambda *args, **kwargs: None

        # Running data through external function
            case "base":
                return add_transaction_cost

            case _:
                return None

    @property
    def handle_memory_data(self: Self):
        """How to process a memory message

        :return: Callable object
        """

        # Just printing the message out
        match self.mode:
            case "console":
                return print

        # Running the message through another function
            case "base":
                return add_memory_messages

            case _:
                return None
