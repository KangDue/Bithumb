import pandas as pd
import numpy as np
import pybithumb
import time
from api_handler import get_bithumb_client

def moving_average_crossover(df, short_window=5, long_window=20):
    """Moving Average Crossover Strategy"""
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    df['signal'] = np.where(df['short_ma'] > df['long_ma'], 1, 0)
    df['position'] = df['signal'].diff()
    return df

def rsi_strategy(df, period=14, overbought=70, oversold=30):
    """RSI Based Strategy"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    df['signal'] = np.where(df['rsi'] < oversold, 1, np.where(df['rsi'] > overbought, -1, 0))
    df['position'] = df['signal'].cumsum()
    return df

def bollinger_bands_strategy(df, window=20, num_std=2):
    """Bollinger Bands Strategy"""
    df['ma'] = df['close'].rolling(window=window).mean()
    df['std'] = df['close'].rolling(window=window).std()
    df['upper'] = df['ma'] + (df['std'] * num_std)
    df['lower'] = df['ma'] - (df['std'] * num_std)
    df['signal'] = np.where(df['close'] < df['lower'], 1, np.where(df['close'] > df['upper'], -1, 0))
    df['position'] = df['signal'].cumsum()
    return df

def backtest(strategy_func, ticker, start, end, interval='minute1', initial_balance=1000000):
    """Backtest a strategy"""
    df = pybithumb.get_ohlcv(ticker, interval=interval)
    df = df.loc[start:end]
    df = strategy_func(df)
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['position'].shift(1) * df['returns']
    df['cum_returns'] = (1 + df['strategy_returns']).cumprod()
    final_balance = initial_balance * df['cum_returns'].iloc[-1]
    return final_balance, df


def live_trade(strategy_func, ticker, interval=60):
    """Live trading loop"""
    client = get_bithumb_client()
    if not client:
        print("API keys not set.")
        return
    position = 0
    while True:
        df = pybithumb.get_ohlcv(ticker, interval='minute1')[-100:]
        df = strategy_func(df)
        signal = df['signal'].iloc[-1]
        if signal == 1 and position == 0:
            # Buy
            balance = client.get_balance(ticker.split('-')[0])
            if balance[2] > 0:  # Available KRW
                amount = balance[2] / df['close'].iloc[-1]
                client.buy_market_order(ticker, amount)
                position = 1
                print("Bought", ticker)
        elif signal == -1 and position == 1:
            # Sell
            balance = client.get_balance(ticker.split('-')[0])
            if balance[0] > 0:  # Available coin
                client.sell_market_order(ticker, balance[0])
                position = 0
                print("Sold", ticker)
        time.sleep(interval)