# Bithumb Auto Trader

## Overview

## 요구사항
- Python 3.11
- uv (가상환경 관리)
- pybithumb, PyQt5, pyqtgraph, pandas, numpy, keyring

## 설치 및 환경 구성

이 프로젝트를 실행하기 위해 다음 단계를 따르세요. Python 3.11을 기반으로 하며, uv를 사용하여 가상환경을 관리합니다.

1. **필수 요구사항 확인**:
   - Python 3.11이 설치되어 있어야 합니다. (없다면 [공식 사이트](https://www.python.org/downloads/)에서 다운로드하세요.)
   - uv가 설치되어 있어야 합니다. (pip install uv로 설치 가능)

2. **가상환경 생성 및 활성화**:
   ```bash
   uv venv .venv --python 3.11
   source .venv/bin/activate  # Linux/Mac
   # 또는 Windows: .venv\Scripts\activate
   ```

3. **필요 패키지 설치**:
   ```bash
   uv pip install pybithumb pyqt5 pyqtgraph pandas numpy keyring
   ```

## 실행 방법

1. 가상환경이 활성화된 상태에서 다음 명령어를 실행하세요:
   ```bash
   python main.py
   ```

2. 프로그램이 실행되면:
   - **API Settings** 탭에서 Bithumb API 키(Connect Key와 Secret Key)를 입력하고 저장하세요. (Bithumb 계정이 필요합니다.)
   - **Strategies** 탭에서 원하는 전략과 코인을 선택한 후 "Start Live Trade" 버튼을 클릭하여 실시간 거래를 시작하세요.
   - **Backtesting** 탭에서 코인, 기간, 간격을 선택하고 "Run Backtest"를 클릭하여 백테스팅을 수행하세요.
   - **Chart** 탭에서 코인과 간격을 선택하여 차트를 로드하고, 실시간 모니터링을 시작할 수 있습니다.
   - **Account** 탭에서 잔고, 주문서, 수수료를 확인하세요.

**주의**: 실제 거래 시 자산 손실 위험이 있으니 테스트 환경에서 충분히 검증하세요. API 키는 안전하게 관리하세요.

## 전략
- Moving Average Crossover
- RSI
- Bollinger Bands

## 백테스팅
과거 데이터를 사용한 전략 성능 테스트

## 주의
실제 거래 시 API 키가 필요하며, 거래 위험을 감수하세요.

## New Features

- **Coin Selection**: Users can select from a list of available tickers using dropdown menus in various tabs.
- **Chart Interval Adjustment**: Adjust the time interval for charts from 1 minute to 24 hours.
- **Account Information**: View balance, order book, and trading fees in the Account tab.
- **Real-time Monitoring**: Use WebSocket to monitor real-time price updates in the Chart tab.