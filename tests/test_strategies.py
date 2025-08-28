import pandas as pd
import numpy as np
from strategies import moving_average_crossover, rsi_strategy, bollinger_bands_strategy

def test_moving_average_crossover():
    data = {'close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]}
    df = pd.DataFrame(data)
    result = moving_average_crossover(df)
    assert 'short_ma' in result.columns
    assert 'long_ma' in result.columns
    assert 'signal' in result.columns
    assert 'position' in result.columns
    assert result['signal'].iloc[-1] == 1  # Assuming increasing trend

def test_rsi_strategy():
    data = {'close': [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]}
    df = pd.DataFrame(data)
    result = rsi_strategy(df)
    assert 'rsi' in result.columns
    assert 'signal' in result.columns
    assert 'position' in result.columns

def test_bollinger_bands_strategy():
    data = {'close': np.random.normal(100, 10, 30)}
    df = pd.DataFrame(data)
    result = bollinger_bands_strategy(df)
    assert 'ma' in result.columns
    assert 'upper' in result.columns
    assert 'lower' in result.columns
    assert 'signal' in result.columns
    assert 'position' in result.columns