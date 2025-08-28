import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTabWidget, QComboBox, QDateEdit, QTextEdit, QHBoxLayout
import api_handler
from strategies import *
import pyqtgraph as pg
from datetime import datetime
import pybithumb
import numpy as np
import json
from pybithumb import WebSocketManager
from PyQt5.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bithumb Auto Trader")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # API Settings Tab
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        api_label = QLabel("API Settings")
        api_layout.addWidget(api_label)

        self.connect_key_input = QLineEdit()
        self.connect_key_input.setPlaceholderText("Enter Connect Key")
        api_layout.addWidget(self.connect_key_input)

        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("Enter Secret Key")
        self.secret_key_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.secret_key_input)

        save_button = QPushButton("Save API Keys")
        save_button.clicked.connect(self.save_api_keys)
        api_layout.addWidget(save_button)

        self.tabs.addTab(api_tab, "API Settings")

        # Strategies Tab
        strategy_tab = QWidget()
        strategy_layout = QVBoxLayout(strategy_tab)
        strategy_label = QLabel("Select Strategy")
        strategy_layout.addWidget(strategy_label)

        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["Moving Average Crossover", "RSI", "Bollinger Bands"])
        strategy_layout.addWidget(self.strategy_combo)

        self.all_tickers = self.get_ticker_list()
        strategy_ticker_layout = QHBoxLayout()
        strategy_ticker_label = QLabel("Ticker:")
        strategy_ticker_layout.addWidget(strategy_ticker_label)
        self.ticker_combo_strategy = QComboBox()
        self.ticker_combo_strategy.addItems(self.all_tickers)
        strategy_ticker_layout.addWidget(self.ticker_combo_strategy)
        self.search_strategy = QLineEdit()
        self.search_strategy.setPlaceholderText("Search Ticker")
        strategy_ticker_layout.addWidget(self.search_strategy)
        self.search_strategy.textChanged.connect(self.filter_strategy)
        strategy_layout.addLayout(strategy_ticker_layout)

        start_trade_button = QPushButton("Start Live Trade")
        start_trade_button.clicked.connect(self.start_live_trade)
        strategy_layout.addWidget(start_trade_button)

        self.tabs.addTab(strategy_tab, "Strategies")

        # Backtesting Tab
        backtest_tab = QWidget()
        backtest_layout = QVBoxLayout(backtest_tab)
        backtest_label = QLabel("Backtesting")
        backtest_layout.addWidget(backtest_label)

        ticker_layout = QHBoxLayout()
        ticker_label = QLabel("Ticker:")
        self.ticker_combo_backtest = QComboBox()
        self.ticker_combo_backtest.addItems(self.get_ticker_list())
        ticker_layout.addWidget(ticker_label)
        ticker_layout.addWidget(self.ticker_combo_backtest)
        self.search_backtest = QLineEdit()
        self.search_backtest.setPlaceholderText("Search Ticker")
        ticker_layout.addWidget(self.search_backtest)
        self.search_backtest.textChanged.connect(self.filter_backtest)
        backtest_layout.addLayout(ticker_layout)

        date_layout = QHBoxLayout()
        start_date_label = QLabel("Start Date:")
        self.start_date = QDateEdit()
        self.start_date.setDate(datetime.now().date())
        end_date_label = QLabel("End Date:")
        self.end_date = QDateEdit()
        self.end_date.setDate(datetime.now().date())
        date_layout.addWidget(start_date_label)
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(end_date_label)
        date_layout.addWidget(self.end_date)
        backtest_layout.addLayout(date_layout)

        interval_layout = QHBoxLayout()
        interval_label = QLabel("Interval:")
        self.interval_combo_backtest = QComboBox()
        self.interval_combo_backtest.addItems(["minute1", "minute3", "minute5", "minute10", "minute30", "hour1", "hour6", "hour12", "hour24"])
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_combo_backtest)
        backtest_layout.addLayout(interval_layout)

        run_backtest_button = QPushButton("Run Backtest")
        run_backtest_button.clicked.connect(self.run_backtest)
        backtest_layout.addWidget(run_backtest_button)

        self.backtest_result = QTextEdit()
        backtest_layout.addWidget(self.backtest_result)

        self.tabs.addTab(backtest_tab, "Backtesting")

        # Chart Tab
        chart_tab = QWidget()
        chart_layout = QVBoxLayout(chart_tab)

        chart_controls = QHBoxLayout()
        ticker_label = QLabel("Ticker:")
        self.ticker_combo_chart = QComboBox()
        self.ticker_combo_chart.addItems(self.get_ticker_list())
        chart_controls.addWidget(ticker_label)
        chart_controls.addWidget(self.ticker_combo_chart)
        self.search_chart = QLineEdit()
        self.search_chart.setPlaceholderText("Search Ticker")
        chart_controls.addWidget(self.search_chart)
        self.search_chart.textChanged.connect(self.filter_chart)

        interval_label = QLabel("Interval:")
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1m", "3m", "5m", "10m", "30m", "1h", "6h", "12h", "24h"])
        chart_controls.addWidget(interval_label)
        chart_controls.addWidget(self.interval_combo)

        load_button = QPushButton("Load Chart")
        load_button.clicked.connect(self.load_chart)
        chart_controls.addWidget(load_button)

        self.realtime_button = QPushButton("Start Real-time Monitoring")
        self.realtime_button.clicked.connect(self.toggle_realtime)
        chart_controls.addWidget(self.realtime_button)

        chart_layout.addLayout(chart_controls)
        self.plot_widget = pg.PlotWidget()
        chart_layout.addWidget(self.plot_widget)
        self.tabs.addTab(chart_tab, "Chart")

        self.ws = None
        self.realtime_data = []
        self.realtime_plot = self.plot_widget.plot(pen='w', name='Real-time Close')
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_realtime_plot)

        # Account Tab
        account_tab = QWidget()
        account_layout = QVBoxLayout(account_tab)
        account_label = QLabel("Account Information")
        account_layout.addWidget(account_label)

        self.all_tickers = self.get_ticker_list()
        account_ticker_layout = QHBoxLayout()
        account_ticker_label = QLabel("Ticker:")
        account_ticker_layout.addWidget(account_ticker_label)
        self.ticker_combo_account = QComboBox()
        self.ticker_combo_account.addItems(self.all_tickers)
        account_ticker_layout.addWidget(self.ticker_combo_account)
        self.search_account = QLineEdit()
        self.search_account.setPlaceholderText("Search Ticker")
        account_ticker_layout.addWidget(self.search_account)
        self.search_account.textChanged.connect(self.filter_account)
        account_layout.addLayout(account_ticker_layout)
        balance_button = QPushButton("Fetch Balance")
        balance_button.clicked.connect(self.fetch_balance)
        account_layout.addWidget(balance_button)
        self.balance_display = QTextEdit()
        account_layout.addWidget(self.balance_display)

        orderbook_button = QPushButton("Fetch Orderbook")
        orderbook_button.clicked.connect(self.fetch_orderbook)
        account_layout.addWidget(orderbook_button)
        self.orderbook_display = QTextEdit()
        account_layout.addWidget(self.orderbook_display)

        fee_button = QPushButton("Fetch Trading Fee")
        fee_button.clicked.connect(self.fetch_fee)
        account_layout.addWidget(fee_button)
        self.fee_display = QTextEdit()
        account_layout.addWidget(self.fee_display)

        self.tabs.addTab(account_tab, "Account")

    def save_api_keys(self):
        connect_key = self.connect_key_input.text()
        secret_key = self.secret_key_input.text()
        if connect_key and secret_key:
            api_handler.set_api_keys(connect_key, secret_key)
            QMessageBox.information(self, "Success", "API Keys saved successfully.")
        else:
            QMessageBox.warning(self, "Error", "Please enter both keys.")

    def start_live_trade(self):
        strategy = self.strategy_combo.currentText()
        ticker = self.ticker_combo_strategy.currentText()
        if not ticker:
            QMessageBox.warning(self, "Error", "Please select a ticker.")
            return
        if strategy == "Moving Average Crossover":
            func = moving_average_crossover
        elif strategy == "RSI":
            func = rsi_strategy
        elif strategy == "Bollinger Bands":
            func = bollinger_bands_strategy
        else:
            return
        # In a real scenario, run in thread
        live_trade(func, ticker)

    def load_chart(self):
        ticker = self.ticker_combo_chart.currentText()
        interval = self.interval_combo.currentText()
        if not ticker or not interval:
            QMessageBox.warning(self, "Error", "Please select ticker and interval.")
            return
        df = pybithumb.get_ohlcv(ticker, interval)
        if df is None or df.empty:
            QMessageBox.warning(self, "Error", "Failed to load chart data for the selected ticker and interval.")
            return
        self.plot_widget.clear()
        x = np.arange(len(df.index))
        self.plot_widget.plot(x, df['close'].values, pen='w', name='Close')
        self.plot_widget.addLegend()

    def run_backtest(self):
        strategy = self.strategy_combo.currentText()
        ticker = self.ticker_combo_backtest.currentText()
        if not ticker:
            QMessageBox.warning(self, "Error", "Please select a ticker.")
            return
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        interval = self.interval_combo_backtest.currentText()
        if strategy == "Moving Average Crossover":
            func = moving_average_crossover
        elif strategy == "RSI":
            func = rsi_strategy
        elif strategy == "Bollinger Bands":
            func = bollinger_bands_strategy
        else:
            return
        final_balance, df = backtest(func, ticker, start, end, interval=interval)
        self.backtest_result.setText(f"Final Balance: {final_balance}")
        # Plot chart with indicators
        self.plot_widget.clear()
        x = np.arange(len(df.index))
        self.plot_widget.plot(x, df['close'].values, pen='w', name='Close')
        if strategy == "Moving Average Crossover":
            self.plot_widget.plot(x, df['short_ma'].values, pen='b', name='Short MA')
            self.plot_widget.plot(x, df['long_ma'].values, pen='r', name='Long MA')
        elif strategy == "RSI":
            self.plot_widget.plot(x, df['rsi'].values, pen='g', name='RSI')
        elif strategy == "Bollinger Bands":
            self.plot_widget.plot(x, df['upper'].values, pen='r', name='Upper BB')
            self.plot_widget.plot(x, df['lower'].values, pen='r', name='Lower BB')
            self.plot_widget.plot(x, df['ma'].values, pen='b', name='MA')
        self.plot_widget.addLegend()

    def get_ticker_list(self):
        return pybithumb.get_tickers()

    def get_bithumb_instance(self):
        conkey, seckey = api_handler.get_api_keys()
        if not conkey or not seckey:
            QMessageBox.warning(self, "Error", "API keys not set.")
            return None
        return pybithumb.Bithumb(conkey, seckey)

    def fetch_balance(self):
        bithumb = self.get_bithumb_instance()
        if bithumb:
            balance = bithumb.get_balance("ALL")
            self.balance_display.setText(json.dumps(balance, indent=4))

    def fetch_orderbook(self):
        ticker = self.ticker_combo_account.currentText()
        if not ticker:
            QMessageBox.warning(self, "Error", "Please select a ticker.")
            return
        orderbook = pybithumb.get_orderbook(ticker)
        self.orderbook_display.setText(json.dumps(orderbook, indent=4))

    def fetch_fee(self):
        ticker = self.ticker_combo_account.currentText()
        if not ticker:
            QMessageBox.warning(self, "Error", "Please select a ticker.")
            return
        bithumb = self.get_bithumb_instance()
        if bithumb:
            fee = bithumb.get_trading_fee(ticker)
            self.fee_display.setText(json.dumps(fee, indent=4))

    def toggle_realtime(self):
        if self.timer.isActive():
            self.timer.stop()
            if self.ws:
                self.ws.terminate()
            self.realtime_button.setText("Start Real-time Monitoring")
        else:
            ticker = self.ticker_combo_chart.currentText()
            if not ticker:
                QMessageBox.warning(self, "Error", "Please select a ticker.")
                return
            self.realtime_data = []
            self.ws = WebSocketManager("ticker", [f"{ticker}_KRW"])
            self.timer.start(1000)  # Update every second
            self.realtime_button.setText("Stop Real-time Monitoring")

    def update_realtime_plot(self):
        msg = self.ws.get()
        if msg:
            close = float(msg['content']['close'])
            self.realtime_data.append(close)
            x = np.arange(len(self.realtime_data))
            self.realtime_plot.setData(x, self.realtime_data)

    def filter_strategy(self, text):
        filtered = [t for t in self.all_tickers if text.lower() in t.lower()]
        self.ticker_combo_strategy.clear()
        self.ticker_combo_strategy.addItems(filtered)

    def filter_backtest(self, text):
        filtered = [t for t in self.all_tickers if text.lower() in t.lower()]
        self.ticker_combo_backtest.clear()
        self.ticker_combo_backtest.addItems(filtered)

    def filter_chart(self, text):
        filtered = [t for t in self.all_tickers if text.lower() in t.lower()]
        self.ticker_combo_chart.clear()
        self.ticker_combo_chart.addItems(filtered)

    def filter_account(self, text):
        filtered = [t for t in self.all_tickers if text.lower() in t.lower()]
        self.ticker_combo_account.clear()
        self.ticker_combo_account.addItems(filtered)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())