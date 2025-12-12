# Crypto Dashboard
A real-time cryptocurrency dashboard disigned for market analysis and trading simulation. This application leverages the Binance WebSocket API to deliver live market data, Interactive technical analysis charting and a comprehensive futures trading simulator with risk management features.

Built with **Python** and **Tkinter** and utilizing **Matplotlib** for high-performance data visualization

## Prerequisites
This project is optimized for **Python 3.11**
Please don't use **Python 3.14 (Pre-release)** as some libraries (numpy/matplotlib) may not support it yet

### Required
**Python 3.11.x** (Recommended)
[Download Python 3.11](https://www.python.org/downloads/release/python-3119/)

### Don't forgot to Check your Python Version
```bash
python --version, py --version
```

## Project Setup Recommended
**Direct Install:**
```bash
1 - py -3.11 -m pip install -r requirements.txt
2 - py -3.11 main.py
```

**Using venv:**
```bash
1 - py -3.11 -m venv venv
2 - .\venv\Scripts\activate
3 - pip install -r requirements.txt
4 - python main.py
```

## Key Features
### Real-time Market Intelligence
**Live Price Streaming:** ```text 
Sub-second price updates via Binance WebSocket API for multiple assets (BTC, ETH, SOL, BNB, DOGE, etc...)```
**Market Statistics:** Real-time displays of 24-hours vol, percentage changes and price direction  
**Order Book and Trades:** Simulated Level 2 market depth and recent trade history feed  

### Interactive Technical Analysis
**Advanced Charting:** Custom implementation of Matplotlib within Tkinter  
**Interactivity:** Full support for zooming, panning, and a dynamic crosshair cursor for precise data inspection  
**Multi-Timeframe:** Seamless switching between timeframes  

### Futures Trading Simulator
**Portfolio Management:** Real-time calculation of Balance, Equity and Margin  
**Order Execution:** Support for **Buy** and **Sell** positions with adjustable leverage  
**Risk Management:** Integrated fields for **Take Profit (TP)** and **Stop Loss (SL)** execution logic  
**Position Tracking:** Live P/L monitoring for open positions with visual profit/loss indicators  

### User Experience
**Responsive Design:** Adaptive layout that scales with window resizing
**Persistence:** Auto-save functionality for user preferences - last selected symbol, timeframe, and visibility settings via `settings.json`
**Modern UI:** "TradingView-style" Dark Theme for reduced eye strain during extended use

## Project Structure
```text
crypto_dashboard/  
├── components/  
│   ├── ticker.py        # Real-time price card widgets  
│   ├── technical.py     # Interactive Matplotlib chart panel  
│   ├── futures.py       # Trading simulator & position management  
│   └── orderbook.py     # Order book and recent trades visualization  
├── utils/  
│   ├── binance_api.py   # REST API wrapper for historical data  
│   └── indicators.py    # Technical analysis calculations (Placeholder)  
├── config.py  
├── main.py              # Application Entry Point  
├── settings.json        # User Preferences Persistence  
└── requirements.txt     # Project Dependencies  
```

## Configuration
The application automatically creates and updates `settings.json` on exit to remember:

- Last viewed cryptocurrency symbol
- Selected timeframe interval
- Visibility state of individual ticker widget

**Customization:** You can modify `config.py` to change the default coin list or adjust the color theme