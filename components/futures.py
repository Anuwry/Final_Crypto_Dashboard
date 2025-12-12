import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import uuid
from datetime import datetime
from config import *
from components.orderbook import OrderBookPanel 

CONTRACT_SIZE = 1 

class FuturesPanel:
    def __init__(self, parent, chart_update_callback):
        self.parent = parent
        self.chart_update_callback = chart_update_callback
        
        self.orders = {} 
        self.rows = {}   
        
        self.balance = 100.00  
        self.equity = 100.00   
        self.total_pl = 0.00     
        self.margin_used = 0.00  
        self.free_margin = 10000.00 
        self.current_prices = {} 
        self.selected_symbol = "btcusdt"
        
        self.frame = tk.Frame(parent, bg=COLOR_SIDEBAR)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.header_frame = tk.Frame(self.frame, bg=COLOR_SIDEBAR, pady=15)
        self.header_frame.pack(fill=tk.X, padx=15)
        
        tk.Label(self.header_frame, text="P/L (Live)", fg=COLOR_TEXT_DIM, bg=COLOR_SIDEBAR, font=("Segoe UI", 9)).pack(anchor="w")
        self.lbl_total_pl = tk.Label(self.header_frame, text="$0.00", fg=COLOR_TEXT_DIM, bg=COLOR_SIDEBAR, font=("Segoe UI", 24, "bold"))
        self.lbl_total_pl.pack(anchor="w")
        
        self.info_frame = tk.Frame(self.header_frame, bg=COLOR_SIDEBAR)
        self.info_frame.pack(anchor="w", fill=tk.X, pady=(10, 0))
        
        self.lbl_balance = tk.Label(self.info_frame, text=f"Balance: ${self.balance:,.2f}", fg=COLOR_TEXT_MAIN, bg=COLOR_SIDEBAR, font=("Segoe UI", 11, "bold"))
        self.lbl_balance.pack(anchor="w")
        
        self.lbl_equity = tk.Label(self.info_frame, text=f"Equity: ${self.equity:,.2f}", fg=COLOR_ACCENT, bg=COLOR_SIDEBAR, font=("Segoe UI", 11, "bold"))
        self.lbl_equity.pack(anchor="w", pady=(2,0))

        self.control_frame = tk.Frame(self.frame, bg=COLOR_CARD, bd=0, relief="flat")
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)

        input_container = tk.Frame(self.control_frame, bg=COLOR_CARD)
        input_container.pack(fill=tk.X, padx=10, pady=10)

        row1 = tk.Frame(input_container, bg=COLOR_CARD)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        row1.grid_columnconfigure(0, weight=1, uniform="group1")
        row1.grid_columnconfigure(1, weight=1, uniform="group1")

        frame_lot = tk.Frame(row1, bg=COLOR_CARD)
        frame_lot.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        tk.Label(frame_lot, text="Lot:", fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, font=("Segoe UI", 8)).pack(anchor="w")
        
        vcmd = (self.frame.register(self.validate_lot_input), '%P')
        self.entry_lot = tk.Entry(frame_lot, bg=COLOR_BG, fg="white", insertbackground="white", 
                                justify="center", font=("Segoe UI", 10),
                                relief="flat", bd=0, 
                                highlightthickness=1, highlightbackground=COLOR_BORDER, highlightcolor=COLOR_ACCENT,
                                validate='key', validatecommand=vcmd)
        self.entry_lot.insert(0, "0.01")
        self.entry_lot.pack(fill=tk.X, ipady=3)

        frame_lev = tk.Frame(row1, bg=COLOR_CARD)
        frame_lev.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        tk.Label(frame_lev, text="Leverage:", fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, font=("Segoe UI", 8)).pack(anchor="w")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Dark.TCombobox", fieldbackground=COLOR_BG, background=COLOR_CARD, foreground="white", arrowcolor="white", bordercolor=COLOR_BORDER, lightcolor=COLOR_BORDER, darkcolor=COLOR_BORDER)
        style.map("Dark.TCombobox", fieldbackground=[("readonly", COLOR_BG)], selectbackground=[("readonly", COLOR_BG)], selectforeground=[("readonly", "white")], foreground=[("readonly", "white")], bordercolor=[("readonly", COLOR_BORDER)])

        self.lev_values = ["1:1", "1:10", "1:25", "1:50", "1:100", "1:200", "1:500"]
        self.combo_lev = ttk.Combobox(frame_lev, values=self.lev_values, justify="center", state="readonly", style="Dark.TCombobox")
        self.combo_lev.set("1:100") 
        self.combo_lev.bind("<<ComboboxSelected>>", lambda e: self.frame.focus())
        self.combo_lev.pack(fill=tk.X, ipady=3)

        row2 = tk.Frame(input_container, bg=COLOR_CARD)
        row2.pack(fill=tk.X, pady=(0, 5))
        tk.Label(row2, text="Take Profit (TP):", fg=COLOR_UP, bg=COLOR_CARD, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.entry_tp = tk.Entry(row2, bg=COLOR_BG, fg=COLOR_UP, insertbackground="white", 
                               justify="center", font=("Segoe UI", 10),
                               relief="flat", bd=0, 
                               highlightthickness=1, highlightbackground=COLOR_BORDER, highlightcolor=COLOR_UP)
        self.entry_tp.pack(fill=tk.X, ipady=3)

        row3 = tk.Frame(input_container, bg=COLOR_CARD)
        row3.pack(fill=tk.X, pady=(0, 10))
        tk.Label(row3, text="Stop Loss (SL):", fg=COLOR_DOWN, bg=COLOR_CARD, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.entry_sl = tk.Entry(row3, bg=COLOR_BG, fg=COLOR_DOWN, insertbackground="white", 
                               justify="center", font=("Segoe UI", 10),
                               relief="flat", bd=0, 
                               highlightthickness=1, highlightbackground=COLOR_BORDER, highlightcolor=COLOR_DOWN)
        self.entry_sl.pack(fill=tk.X, ipady=3)

        btn_row = tk.Frame(self.control_frame, bg=COLOR_CARD)
        btn_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.btn_buy = tk.Button(btn_row, text="BUY", bg=COLOR_ACCENT, fg="white", bd=0, font=FONT_BOLD, cursor="hand2", command=lambda: self.place_order("BUY"))
        self.btn_buy.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3), ipady=5)
        self.btn_sell = tk.Button(btn_row, text="SELL", bg=COLOR_DOWN, fg="white", bd=0, font=FONT_BOLD, cursor="hand2", command=lambda: self.place_order("SELL"))
        self.btn_sell.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0), ipady=5)

        self.tab_header_frame = tk.Frame(self.frame, bg=COLOR_SIDEBAR)
        self.tab_header_frame.pack(fill=tk.X, padx=15, pady=(20, 5))

        self.lbl_tab_pos = tk.Label(self.tab_header_frame, text="Positions", bg=COLOR_SIDEBAR, fg="white", font=("Segoe UI", 10, "bold"), cursor="hand2")
        self.lbl_tab_pos.pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_tab_pos.bind("<Button-1>", lambda e: self.switch_tab("positions"))

        self.lbl_tab_hist = tk.Label(self.tab_header_frame, text="History", bg=COLOR_SIDEBAR, fg=COLOR_TEXT_DIM, font=("Segoe UI", 10), cursor="hand2")
        self.lbl_tab_hist.pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_tab_hist.bind("<Button-1>", lambda e: self.switch_tab("history"))

        self.lbl_tab_others = tk.Label(self.tab_header_frame, text="Others", bg=COLOR_SIDEBAR, fg=COLOR_TEXT_DIM, font=("Segoe UI", 10), cursor="hand2")
        self.lbl_tab_others.pack(side=tk.LEFT)
        self.lbl_tab_others.bind("<Button-1>", lambda e: self.switch_tab("others"))

        self.content_container = tk.Frame(self.frame, bg=COLOR_SIDEBAR)
        self.content_container.pack(fill=tk.BOTH, expand=True)

        self.page_positions = tk.Frame(self.content_container, bg=COLOR_SIDEBAR)
        self.scroll_pos, self.frame_pos = self._create_scrollable_area(self.page_positions)
        
        self.page_history = tk.Frame(self.content_container, bg=COLOR_SIDEBAR)
        self.scroll_hist, self.frame_hist = self._create_scrollable_area(self.page_history)

        self.page_others = tk.Frame(self.content_container, bg=COLOR_SIDEBAR)
        
        self.orderbook_panel = OrderBookPanel(self.page_others) 
        self.current_tab = "positions"
        self.page_positions.pack(fill=tk.BOTH, expand=True)

        self.current_prices = {} 
        self.selected_symbol = "btcusdt"

    def validate_lot_input(self, new_value):
        if new_value == "": return True 
        try:
            val = float(new_value)
            if val > 50: return False
            if "." in new_value:
                if len(new_value.split(".")[1]) > 2: return False
            return True
        except ValueError: return False

    def set_symbol(self, symbol):
        self.selected_symbol = symbol
        self._sync_chart_lines()

    def place_order(self, side):
        try: lot = float(self.entry_lot.get())
        except: return
        if lot < 0.01: return

        try: tp = float(self.entry_tp.get())
        except: tp = 0.0
        try: sl = float(self.entry_sl.get())
        except: sl = 0.0

        symbol = self.selected_symbol
        if symbol not in self.current_prices: return
        
        entry_price = self.current_prices[symbol]
        lev_str = self.combo_lev.get() 
        leverage = int(lev_str.split(":")[1])
        required_margin = (entry_price * lot * CONTRACT_SIZE) / leverage
        
        if required_margin > self.free_margin: return

        order_id = str(uuid.uuid4())
        self.orders[order_id] = {
            "symbol": symbol, "side": side, "lot": lot, "leverage": leverage,
            "entry": entry_price, "margin": required_margin, "sl": sl, "tp": tp,
            "time": datetime.now().strftime("%H:%M:%S")
        }
        
        self._create_order_row(order_id)
        self._recalculate_portfolio()
        self._sync_chart_lines()
        self.switch_tab("positions")

    def _create_order_row(self, order_id):
        data = self.orders[order_id]
        row = tk.Frame(self.frame_pos, bg=COLOR_SIDEBAR, pady=2)
        row.pack(fill=tk.X, padx=0)
        
        line1 = tk.Frame(row, bg=COLOR_SIDEBAR)
        line1.pack(fill=tk.X)
        color_side = COLOR_ACCENT if data["side"] == "BUY" else COLOR_DOWN
        
        tk.Label(line1, text=f"{data['symbol'].upper()}", fg="white", bg=COLOR_SIDEBAR, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(line1, text=f" {data['side']}", fg=color_side, bg=COLOR_SIDEBAR, font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT)
        tk.Label(line1, text=f" {data['lot']}", fg=COLOR_TEXT_DIM, bg=COLOR_SIDEBAR, font=("Segoe UI", 8)).pack(side=tk.LEFT)
        lbl_pl = tk.Label(line1, text="0.00", fg=COLOR_TEXT_MAIN, bg=COLOR_SIDEBAR, font=("Segoe UI", 9, "bold"))
        lbl_pl.pack(side=tk.RIGHT)

        line2 = tk.Frame(row, bg=COLOR_SIDEBAR)
        line2.pack(fill=tk.X)
        info_text = f"@{data['entry']:.2f}"
        if data['tp'] > 0: info_text += f" TP:{data['tp']}"
        if data['sl'] > 0: info_text += f" SL:{data['sl']}"
        
        lbl_price_info = tk.Label(line2, text=info_text, fg=COLOR_TEXT_DIM, bg=COLOR_SIDEBAR, font=("Segoe UI", 7))
        lbl_price_info.pack(side=tk.LEFT)
        
        btn_close = tk.Button(line2, text="✕", bg=COLOR_SIDEBAR, fg=COLOR_TEXT_DIM, bd=0, font=("Arial", 8), cursor="hand2",
                              activebackground=COLOR_DOWN, activeforeground="white",
                              command=lambda: self.close_order(order_id))
        btn_close.pack(side=tk.RIGHT)

        separator = tk.Frame(self.frame_pos, bg=COLOR_BORDER, height=1)
        separator.pack(fill=tk.X, pady=5)

        self.rows[order_id] = {
            "frame": row, "separator": separator, 
            "lbl_pl": lbl_pl, "lbl_price_info": lbl_price_info
        }

    def _create_history_row(self, data, profit):
        row = tk.Frame(self.frame_hist, bg=COLOR_SIDEBAR, pady=2)
        row.pack(fill=tk.X, padx=0)
        
        line1 = tk.Frame(row, bg=COLOR_SIDEBAR)
        line1.pack(fill=tk.X)
        color_side = COLOR_ACCENT if data["side"] == "BUY" else COLOR_DOWN
        color_pl = "#00bfff" if profit >= 0 else COLOR_DOWN
        
        tk.Label(line1, text=f"{data['symbol'].upper()}", fg="white", bg=COLOR_SIDEBAR, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(line1, text=f" {data['side']}", fg=color_side, bg=COLOR_SIDEBAR, font=("Segoe UI", 8)).pack(side=tk.LEFT)
        tk.Label(line1, text=f"{profit:+.2f}", fg=color_pl, bg=COLOR_SIDEBAR, font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT)
        
        line2 = tk.Frame(row, bg=COLOR_SIDEBAR)
        line2.pack(fill=tk.X)
        tk.Label(line2, text=f"Lot: {data['lot']} @ {data['entry']:.2f}", fg=COLOR_TEXT_DIM, bg=COLOR_SIDEBAR, font=("Segoe UI", 8)).pack(side=tk.LEFT)
        tk.Label(line2, text=f"{data['time']}", fg=COLOR_TEXT_DIM, bg=COLOR_SIDEBAR, font=("Segoe UI", 8)).pack(side=tk.RIGHT)

        tk.Frame(self.frame_hist, bg=COLOR_BORDER, height=1).pack(fill=tk.X, pady=5)

    def close_order(self, order_id):
        if order_id in self.orders:
            data = self.orders[order_id]
            current = self.current_prices.get(data['symbol'], data['entry'])
            diff = current - data['entry']
            if data["side"] == "SELL": diff = -diff
            profit = diff * data['lot'] * CONTRACT_SIZE
            
            self.balance += profit
            self.lbl_balance.config(text=f"Balance: ${self.balance:,.2f}")
            
            self._create_history_row(data, profit)
            
            del self.orders[order_id]
            
            if order_id in self.rows:
                self.rows[order_id]["frame"].destroy()
                self.rows[order_id]["separator"].destroy()
                del self.rows[order_id]
            
            self._recalculate_portfolio()
            self._sync_chart_lines()

    def update_price(self, symbol, current_price):
        self.current_prices[symbol] = current_price
        
        if self.current_tab == "others":
            self.orderbook_panel.update_data(current_price)

        orders_to_close = []
        for order_id, data in self.orders.items():
            if data["symbol"] == symbol:
                entry = data["entry"]
                lot = data["lot"]
                side = data["side"]
                tp = data["tp"]
                sl = data["sl"]
                
                hit = False
                if side == "BUY":
                    if tp > 0 and current_price >= tp: hit = True
                    if sl > 0 and current_price <= sl: hit = True
                elif side == "SELL":
                    if tp > 0 and current_price <= tp: hit = True
                    if sl > 0 and current_price >= sl: hit = True
                
                if hit:
                    orders_to_close.append(order_id)
                    continue

                diff = current_price - entry
                if side == "SELL": diff = -diff
                profit = diff * lot * CONTRACT_SIZE
                
                widgets = self.rows[order_id]
                color = "#00bfff" if profit >= 0 else COLOR_DOWN 
                widgets["lbl_pl"].config(text=f"{profit:+.2f}", fg=color)
        
        for oid in orders_to_close:
            self.close_order(oid)
            
        self._recalculate_portfolio()

    def _recalculate_portfolio(self):
        total_floating_pl = 0.0
        total_margin_used = 0.0
        
        for order_id, data in self.orders.items():
            symbol = data["symbol"]
            total_margin_used += data["margin"]
            if symbol in self.current_prices:
                current = self.current_prices[symbol]
                diff = current - data["entry"]
                if data["side"] == "SELL": diff = -diff
                total_floating_pl += (diff * data["lot"] * CONTRACT_SIZE)
        
        self.equity = self.balance + total_floating_pl
        self.margin_used = total_margin_used
        self.free_margin = self.equity - self.margin_used
        
        if total_floating_pl == 0:
            self.lbl_total_pl.config(text="$0.00", fg=COLOR_TEXT_DIM)
        elif total_floating_pl > 0:
            self.lbl_total_pl.config(text=f"+${total_floating_pl:,.2f}", fg="#00bfff")
        else:
            self.lbl_total_pl.config(text=f"-${abs(total_floating_pl):,.2f}", fg=COLOR_DOWN)
        
        self.lbl_equity.config(text=f"Equity: ${self.equity:,.2f}")

    def _sync_chart_lines(self):
        active_lines = []
        for order_id, data in self.orders.items():
            if data['symbol'] == self.selected_symbol:
                active_lines.append(data)
        self.chart_update_callback(active_lines)

    def switch_tab(self, tab_name):
        if self.current_tab == tab_name: return
        self.current_tab = tab_name
        
        self.lbl_tab_pos.config(fg=COLOR_TEXT_DIM, font=("Segoe UI", 10))
        self.lbl_tab_hist.config(fg=COLOR_TEXT_DIM, font=("Segoe UI", 10))
        self.lbl_tab_others.config(fg=COLOR_TEXT_DIM, font=("Segoe UI", 10))
        
        self.page_positions.pack_forget()
        self.page_history.pack_forget()
        self.page_others.pack_forget()

        if tab_name == "positions":
            self.lbl_tab_pos.config(fg="white", font=("Segoe UI", 10, "bold"))
            self.page_positions.pack(fill=tk.BOTH, expand=True)
        elif tab_name == "history":
            self.lbl_tab_hist.config(fg="white", font=("Segoe UI", 10, "bold"))
            self.page_history.pack(fill=tk.BOTH, expand=True)
        elif tab_name == "others":
            self.lbl_tab_others.config(fg="white", font=("Segoe UI", 10, "bold"))
            self.page_others.pack(fill=tk.BOTH, expand=True)

    def _create_scrollable_area(self, parent):
        canvas = tk.Canvas(parent, bg=COLOR_SIDEBAR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_SIDEBAR)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=220)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=5)
        scrollbar.pack(side="right", fill="y")
        return canvas, scrollable_frame