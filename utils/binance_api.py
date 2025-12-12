import requests
import time

def get_kline_data(symbol, interval="1m", limit=1000, retries=3):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
     
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            candles = []
            for x in data:
                candles.append({
                    "time": x[0],
                    "open": float(x[1]),
                    "high": float(x[2]),
                    "low": float(x[3]),
                    "close": float(x[4])
                })
            return candles
        except Exception as e:
            print(f"[API] Error {symbol}: {e}")
            time.sleep(1)
    return []