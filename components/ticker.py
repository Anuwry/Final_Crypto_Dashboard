import tkinter as tk
import threading
import json
import websocket
from config import *

class CryptoTicker:
    def __init__(self, parent, symbol, name, chart_callback, on_update_callback=None):
        self.symbol = symbol.lower()
        self.name = name
        self.chart_callback = chart_callback
        self.on_update_callback = on_update_callback
        self.ws = None
        self.is_running = False
        
        self.frame = tk.Frame(parent, bg=COLOR_CARD, bd=1, relief="solid")
        self.frame.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.frame.bind("<Button-1>", lambda e: self.chart_callback(self.symbol))

        self.lbl_name = tk.Label(self.frame, text=self.name.upper(), bg=COLOR_CARD, fg=COLOR_TEXT_DIM, font=FONT_TITLE, anchor="w")
        self.lbl_name.pack(fill=tk.X, padx=10, pady=(10, 0))
        self.lbl_price = tk.Label(self.frame, text="---", bg=COLOR_CARD, fg=COLOR_TEXT_MAIN, font=FONT_PRICE, anchor="w")
        self.lbl_price.pack(fill=tk.X, padx=10, pady=0)
        self.lbl_change = tk.Label(self.frame, text="--", bg=COLOR_CARD, fg=COLOR_TEXT_MAIN, font=FONT_MAIN, anchor="w")
        self.lbl_change.pack(fill=tk.X, padx=10, pady=(0, 2))
        self.lbl_volume = tk.Label(self.frame, text="Vol: --", bg=COLOR_CARD, fg=COLOR_TEXT_DIM, font=("Segoe UI", 8), anchor="w")
        self.lbl_volume.pack(fill=tk.X, padx=10, pady=(0, 10))

        for widget in [self.lbl_name, self.lbl_price, self.lbl_change, self.lbl_volume]:
            widget.bind("<Button-1>", lambda e: self.chart_callback(self.symbol))

    def set_highlight(self, is_active):
        if is_active: self.frame.config(highlightbackground=COLOR_ACCENT, highlightthickness=2)
        else: self.frame.config(highlightbackground=COLOR_BORDER, highlightthickness=1)

    def start(self):
        if self.is_running: return
        self.is_running = True
        url = f"wss://stream.binance.com:9443/ws/{self.symbol}@ticker"
        self.ws = websocket.WebSocketApp(url, on_message=self.on_message, on_error=lambda ws, err: print(f"Error {self.symbol}"), on_close=lambda ws, s, m: print(f"Closed {self.symbol}"))
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def stop(self):
        self.is_running = False
        if self.ws: self.ws.close()

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            price = float(data['c'])
            change = float(data['p'])
            percent = float(data['P'])
            volume = float(data['q'])
            self.lbl_price.after(0, self.update_ui, price, change, percent, volume)
        except: pass

    def update_ui(self, price, change, percent, volume):
        color = COLOR_UP if change >= 0 else COLOR_DOWN
        sign = "+" if change >= 0 else ""
        self.lbl_price.config(text=f"{price:,.2f}")
        self.lbl_change.config(text=f"{sign}{change:.2f} ({sign}{percent:.2f}%)", fg=color)
        if volume > 1000000: vol_str = f"{volume/1000000:.2f}M"
        elif volume > 1000: vol_str = f"{volume/1000:.2f}K"
        else: vol_str = f"{volume:.2f}"
        self.lbl_volume.config(text=f"Vol: {vol_str} USDT")
        if self.on_update_callback: self.on_update_callback(self.symbol, price)
 
    def show(self):
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.start()

    def hide(self):
        self.stop()
        self.frame.pack_forget()