import requests

def test_rest_api():
    """Test basic REST API connectivity."""
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": "BTCUSDT"}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✓ REST API works: BTC = ${data['price']}")
        return True
    except Exception as e:
        print(f"✗ REST API failed: {e}")
        return False

def test_websocket():
    """Test basic WebSocket connectivity."""
    import websocket
    import json
    
    received_data = False
    
    def on_message(ws, message):
        nonlocal received_data
        data = json.loads(message)
        print(f"✓ WebSocket works: BTC = ${data['c']}")
        received_data = True
        ws.close()
    
    def on_error(ws, error):
        print(f"✗ WebSocket failed: {error}")
    
    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@ticker",
        on_message=on_message,
        on_error=on_error
    )
    
    # Run for max 5 seconds
    import threading
    thread = threading.Thread(target=ws.run_forever)
    thread.daemon = True
    thread.start()
    thread.join(timeout=5)
    
    return received_data

if __name__ == "__main__":
    print("Testing Binance API connectivity...\n")
    rest_ok = test_rest_api()
    ws_ok = test_websocket()
    
    if rest_ok and ws_ok:
        print("\n✓ All tests passed! Ready to build dashboard.")
    else:
        print("\n✗ Some tests failed. Check your internet connection.")