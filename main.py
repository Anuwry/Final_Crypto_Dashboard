import tkinter as tk
from tkinter import ttk
import json
import os
from config import *
from components.ticker import CryptoTicker
from components.technical import TechnicalAnalysisPanel
from components.futures import FuturesPanel

SETTINGS_FILE = "settings.json"
 
class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro Crypto Dashboard")
        self.root.geometry("1200x850")
        self.root.configure(bg=COLOR_BG)

        self.settings = self.load_settings()
        self.current_chart_symbol = self.settings.get("symbol", DEFAULT_COINS[0][0])
        self.current_interval = self.settings.get("interval", "1m")
        saved_visibility = self.settings.get("visibility", {})

        self.sidebar = tk.Frame(root, bg=COLOR_SIDEBAR, width=240)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.futures_panel = FuturesPanel(self.sidebar, self.update_chart_orders)

        self.content_area = tk.Frame(root, bg=COLOR_BG)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.ctrl_frame = tk.Frame(self.content_area, bg=COLOR_BG)
        self.ctrl_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", background=COLOR_CARD, foreground="white", borderwidth=0, focuscolor=COLOR_CARD)
        style.map("TButton", background=[("active", COLOR_BORDER)])

        for symbol, name in DEFAULT_COINS:
            btn = ttk.Button(self.ctrl_frame, text=f"Toggle {symbol.upper()[:3]}", 
                           command=lambda s=symbol: self.toggle_ticker(s))
            btn.pack(side=tk.LEFT, padx=(0, 5))

        self.ticker_wrapper = tk.Frame(self.content_area, bg=COLOR_BG)
        self.ticker_wrapper.pack(fill=tk.X, pady=10, padx=10)
        self.center_frame = tk.Frame(self.ticker_wrapper, bg=COLOR_BG)
        self.center_frame.pack(anchor=tk.W)

        self.chart_panel = TechnicalAnalysisPanel(self.content_area)
        self.chart_panel.show()

        self.futures_panel.set_symbol(self.current_chart_symbol)

        self.tickers = {}
        self.visible_status = {}
        
        for symbol, name in DEFAULT_COINS:
            self.tickers[symbol] = CryptoTicker(self.center_frame, symbol, name, 
                self.on_card_click, on_update_callback=self.on_price_update)
            is_visible = saved_visibility.get(symbol, True)
            self.visible_status[symbol] = is_visible

        self.refresh_ticker_layout()
        if not self.visible_status.get(self.current_chart_symbol, True):
             next_sym = self.find_next_visible_symbol(self.current_chart_symbol)
             if next_sym: self.current_chart_symbol = next_sym
        
        self.select_chart(self.current_chart_symbol)
        self.chart_panel.fetch_and_draw(self.current_chart_symbol, self.current_interval)

    def update_chart_orders(self, orders_data):
        if hasattr(self, 'chart_panel'):
            self.chart_panel.update_active_orders(orders_data)

    def find_next_visible_symbol(self, current_sym):
        symbols = [s for s, n in DEFAULT_COINS]
        try: start_idx = symbols.index(current_sym)
        except: start_idx = -1
        for i in range(start_idx + 1, len(symbols)):
            s = symbols[i]
            if self.visible_status.get(s, True): return s
        for i in range(0, start_idx):
            s = symbols[i]
            if self.visible_status.get(s, True): return s
        return None

    def refresh_ticker_layout(self):
        for t in self.tickers.values(): t.hide()
        for symbol, _ in DEFAULT_COINS:
            if self.visible_status[symbol]:
                self.tickers[symbol].frame.pack(side=tk.LEFT, padx=(0, 10), pady=5)
                self.tickers[symbol].start()

    def toggle_ticker(self, symbol):
        self.visible_status[symbol] = not self.visible_status[symbol]
        self.refresh_ticker_layout()
        if symbol == self.current_chart_symbol and not self.visible_status[symbol]:
            next_symbol = self.find_next_visible_symbol(symbol)
            if next_symbol:
                self.select_chart(next_symbol)
                if not self.chart_panel.show_candles_flag: self.chart_panel.toggle_candles()
            else:
                if self.chart_panel.show_candles_flag: self.chart_panel.toggle_candles()
        elif self.visible_status[symbol]:
            if not self.chart_panel.show_candles_flag:
                self.select_chart(symbol)
                self.chart_panel.toggle_candles()

    def select_chart(self, symbol):
        self.current_chart_symbol = symbol
        for s, ticker in self.tickers.items():
            if s == symbol: ticker.set_highlight(True)
            else: ticker.set_highlight(False)
        
        current_int = self.chart_panel.current_interval
        self.chart_panel.fetch_and_draw(symbol, current_int)
        self.futures_panel.set_symbol(symbol)

    def on_card_click(self, symbol):
        self.select_chart(symbol)

    def on_price_update(self, symbol, price):
        if symbol == self.current_chart_symbol: 
            self.chart_panel.update_current_price(price)
        self.futures_panel.update_price(symbol, price)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f: return json.load(f)
            except: pass
        return {}

    def save_settings(self):
        current_interval = self.chart_panel.current_interval
        data = {"symbol": self.current_chart_symbol, "interval": current_interval, "visibility": self.visible_status}
        try:
            with open(SETTINGS_FILE, "w") as f: json.dump(data, f)
        except Exception as e: print(f"Save Error: {e}")

    def on_close(self):
        self.save_settings()
        for t in self.tickers.values(): t.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()