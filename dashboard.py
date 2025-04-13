import dash
import threading
from dash import dcc, html
from dash.dependencies import Input, Output
from waitress import serve
import plotly.graph_objs as go

from config import DashServer, Styles

# Dash app initialization
app = dash.Dash(__name__, server=True, update_title="", assets_folder="images")
app.title = "Crypto Autotrader Dashboard"
app._favicon = "logo-modified.png"

# Thread-safe module-global / program-local data storage
_data_lock: threading.Lock = threading.Lock()
_info_messages: list[str] = []
_memory_messages: list[str] = []
_transaction_costs: list[float] = []


# Thread-safe functions for modifying data
def add_transaction_cost(cost: float) -> None:
    """Thread-safe function to add a transaction cost.

    :param cost: float to add to local storage of transaction costs (deal values)
    :return: None
    """

    with _data_lock:
        _transaction_costs.append(cost)
        if len(_transaction_costs) > 50:
            _transaction_costs.pop(0)


def add_info_message(message: str) -> None:
    """Thread-safe function to add an info message.

    :param message: string to add to local storage of info messages
    :return: None
    """

    with _data_lock:
        _info_messages.append(message)


def add_memory_messages(memory_message: str) -> None:
    """
    Thread-safe function to add an info message.

    :param memory_message: string to add to local storage
                        (instance of Python's set class) of memory messages
    :return: None
    """

    with _data_lock:
        _memory_messages.append(memory_message)

        # Keep memory storage to only include a single message
        if len(_memory_messages) > 1:
            _memory_messages.pop(0)


def get_transaction_costs() -> list[float]:
    """Thread-safe function to retrieve transaction costs.

    :return: list of floating point numbers
    """

    with _data_lock:
        return _transaction_costs


def get_info_messages() -> list[str]:
    """Thread-safe function to retrieve info messages.

    :return: list of strings
    """

    with _data_lock:
        return _info_messages


def get_memory_messages() -> list[str]:
    """Thread-safe function to retrieve info messages.

    :return: list of strings
    """

    with _data_lock:
        return _memory_messages


# Define Dashboard Layout
app.layout = html.Div([
    html.H1("Crypto Autotrader Dashboard", style=Styles.HEADER),

    # Memory Usage Display
    html.Div([
        html.H3("Memory Usage", style=Styles.GENERIC_FONT),
        html.P(id="memory-usage", style=Styles.PARAGRAPH)
    ], style=Styles.GENERIC_DIV),

    # Transaction Cost Chart
    html.Div([
        html.H3("Transaction Cost Over Time", style=Styles.GENERIC_FONT),
        dcc.Graph(id="transaction-cost-chart")
    ], style=Styles.GENERIC_DIV),

    # Notifications
    html.Div([
        html.H3("Latest Notifications", style=Styles.GENERIC_FONT),
        html.Ul(id="info-messages", style=Styles.UNORDERED_LIST)
    ], style=Styles.GENERIC_DIV),

    # Miscellaneous
    html.Div([
        html.H3("Support developers of Crypto Autotrader", style=Styles.GENERIC_FONT),
        html.A(
            children=[html.Img(
                id="support-banner",
                src="https://nowpayments.io/images/embeds/donation-button-white.svg",
                alt="Cryptocurrency & Bitcoin donation button by NOWPayments"
            )],
            href="https://nowpayments.io/donation/cryptoautotrader",
            target="_blank",
            rel="noreferrer noopener"
        )
    ], style=Styles.HEADER),

    # Live update intervals
    dcc.Interval(id="interval-component", interval=10000, n_intervals=0)
], style=Styles.INTERVAL)


# Callback to update memory usage
@app.callback(
    Output("memory-usage", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_memory_usage(_):
    return get_memory_messages()[-1]


# Callback to update transaction cost chart
@app.callback(
    Output("transaction-cost-chart", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_transaction_cost_chart(_):
    transaction_costs = get_transaction_costs()
    fig = go.Figure()

    if transaction_costs:
        fig.add_trace(go.Scatter(
            y=transaction_costs, mode="lines+markers", name="Transaction Cost",
            line=dict(color="green")
        ))
    else:
        fig.add_trace(go.Scatter(y=[], mode="lines+markers", name="No Data"))

    fig.update_layout(
        title="Transaction Costs Over Time",
        xaxis_title="Transaction Count",
        yaxis_title="Cost",
        template="plotly_dark"
    )
    return fig


# Callback to update info messages
@app.callback(
    Output("info-messages", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_info_messages(_):
    messages = get_info_messages()
    return [html.Li(html.Pre(msg)) for msg in messages[-10:]]


def run_dashboard():
    """Start the Dash server in parallel."""

    parallel_target_kwargs: dict = {
        "app": app.server,
        "host": DashServer.HOST,
        "port": DashServer.PORT,
        "threads": 8
    }

    threading.Thread(
        target=serve,
        kwargs=parallel_target_kwargs,
        daemon=True
    ).start()
