import tkinter as tk
import random
from datetime import datetime
from config import *

class OrderBookPanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=COLOR_SIDEBAR)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.ob_asks_labels = []
        self.ob_bids_labels = []
        self.trades_labels = []
        self._init_ui()
        
    def _init_ui(self):
        tk.Label(self.frame, text="Order Book (Top 10)", fg=COLOR_TEXT_MAIN, bg=COLOR_SIDEBAR, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ob_frame = tk.Frame(self.frame, bg=COLOR_SIDEBAR)
        ob_frame.pack(fill=tk.X, padx=10)
        row_h = tk.Frame(ob_frame, bg=COLOR_SIDEBAR)
        row_h.pack(fill=tk.X)
        tk.Label(row_h, text="Price", fg=COLOR_TEXT_DIM, bg=COLOR_SIDEBAR, width=12, anchor="w").pack(side=tk.LEFT)
        tk.Label(row_h, text="Amount", fg=COLOR_TEXT_DIM, bg=COLOR_SIDEBAR, width=10, anchor="e").pack(side=tk.RIGHT)
        for i in range(5):
            row = tk.Frame(ob_frame, bg=COLOR_SIDEBAR)
            row.pack(fill=tk.X)
            lbl_p = tk.Label(row, text="---", fg=COLOR_DOWN, bg=COLOR_SIDEBAR, width=12, anchor="w", font=("Segoe UI", 8))
            lbl_p.pack(side=tk.LEFT)
            lbl_a = tk.Label(row, text="---", fg=COLOR_TEXT_MAIN, bg=COLOR_SIDEBAR, width=10, anchor="e", font=("Segoe UI", 8))
            lbl_a.pack(side=tk.RIGHT)
            self.ob_asks_labels.insert(0, (lbl_p, lbl_a))
        for i in range(5):
            row = tk.Frame(ob_frame, bg=COLOR_SIDEBAR)
            row.pack(fill=tk.X)
            lbl_p = tk.Label(row, text="---", fg=COLOR_UP, bg=COLOR_SIDEBAR, width=12, anchor="w", font=("Segoe UI", 8))
            lbl_p.pack(side=tk.LEFT)
            lbl_a = tk.Label(row, text="---", fg=COLOR_TEXT_MAIN, bg=COLOR_SIDEBAR, width=10, anchor="e", font=("Segoe UI", 8))
            lbl_a.pack(side=tk.RIGHT)
            self.ob_bids_labels.append((lbl_p, lbl_a))
        tk.Label(self.frame, text="Recent Trades", fg=COLOR_TEXT_MAIN, bg=COLOR_SIDEBAR, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(15, 5))
        trades_frame = tk.Frame(self.frame, bg=COLOR_SIDEBAR)
        trades_frame.pack(fill=tk.X, padx=10)
        for i in range(5):
            row = tk.Frame(trades_frame, bg=COLOR_SIDEBAR)
            row.pack(fill=tk.X)
            lbl_p = tk.Label(row, text="---", fg=COLOR_TEXT_MAIN, bg=COLOR_SIDEBAR, width=10, anchor="w", font=("Segoe UI", 8))
            lbl_p.pack(side=tk.LEFT)
            lbl_a = tk.Label(row, text="---", fg=COLOR_TEXT_DIM, bg=COLOR_SIDEBAR, width=8, anchor="e", font=("Segoe UI", 8))
            lbl_a.pack(side=tk.RIGHT)
            lbl_t = tk.Label(row, text="--:--:--", fg=COLOR_TEXT_DIM, bg=COLOR_SIDEBAR, width=8, anchor="e", font=("Segoe UI", 8))
            lbl_t.pack(side=tk.RIGHT)
            self.trades_labels.append((lbl_p, lbl_a, lbl_t))

    def update_data(self, price):
        spread = price * 0.0002
        for i, (lbl_p, lbl_a) in enumerate(self.ob_asks_labels):
            ask_price = price + spread + (i * spread)
            vol = random.uniform(0.1, 2.0)
            lbl_p.config(text=f"{ask_price:,.2f}")
            lbl_a.config(text=f"{vol:.4f}")
        for i, (lbl_p, lbl_a) in enumerate(self.ob_bids_labels):
            bid_price = price - spread - (i * spread)
            vol = random.uniform(0.1, 2.0)
            lbl_p.config(text=f"{bid_price:,.2f}")
            lbl_a.config(text=f"{vol:.4f}")
        if random.random() > 0.5:
            side = "BUY" if random.random() > 0.5 else "SELL"
            color = COLOR_UP if side == "BUY" else COLOR_DOWN
            trade_price = price + random.uniform(-spread, spread)
            vol = random.uniform(0.01, 0.5)
            time_str = datetime.now().strftime("%H:%M:%S")
            for i in range(len(self.trades_labels)-1, 0, -1):
                p_prev, a_prev, t_prev = self.trades_labels[i-1]
                p_curr, a_curr, t_curr = self.trades_labels[i]
                p_curr.config(text=p_prev.cget("text"), fg=p_prev.cget("fg"))
                a_curr.config(text=a_prev.cget("text"))
                t_curr.config(text=t_prev.cget("text"))
            lbl_p, lbl_a, lbl_t = self.trades_labels[0]
            lbl_p.config(text=f"{trade_price:,.2f}", fg=color)
            lbl_a.config(text=f"{vol:.4f}")
            lbl_t.config(text=time_str)