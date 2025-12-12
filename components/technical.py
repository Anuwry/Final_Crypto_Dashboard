import tkinter as tk
import threading
import time
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.transforms as transforms
from matplotlib.ticker import FuncFormatter
from matplotlib.collections import LineCollection, PolyCollection
from config import *
from utils.binance_api import get_kline_data

matplotlib.rc('font', family='Segoe UI', size=8)

class TechnicalAnalysisPanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=COLOR_BG)
        
        self.figure, self.ax = plt.subplots(figsize=(8, 4), dpi=100)
        self.figure.patch.set_facecolor(COLOR_BG)
        self.ax.set_facecolor(COLOR_BG)
        self.ax.yaxis.tick_right()
        
        self.figure.subplots_adjust(left=0.00, right=0.93, top=0.92, bottom=0.05)
        
        for spine in self.ax.spines.values():
            spine.set_color(COLOR_BORDER)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.canvas_widget.configure(bg=COLOR_BG, highlightthickness=0)

        self.overlay_frame = tk.Frame(self.frame, bg=COLOR_BG)
        self.overlay_frame.place(x=0, y=5)

        self.lbl_symbol = tk.Label(self.overlay_frame, text="SYMBOL", bg=COLOR_BG, fg=COLOR_TEXT_MAIN, font=("Segoe UI", 11, "bold"))
        self.lbl_symbol.pack(side=tk.LEFT, padx=(5, 15))

        self.tf_buttons = {}
        intervals = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]
        for tf in intervals:
            btn = tk.Button(self.overlay_frame, text=tf, bg=COLOR_BG, fg=COLOR_TEXT_DIM, 
                            bd=0, font=("Segoe UI", 9), width=3, cursor="hand2",
                            activebackground=COLOR_CARD, activeforeground=COLOR_ACCENT,
                            command=lambda t=tf: self.change_timeframe(t))
            btn.pack(side=tk.LEFT, padx=0)
            self.tf_buttons[tf] = btn
            
        tk.Label(self.overlay_frame, text="|", bg=COLOR_BG, fg=COLOR_BORDER, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

        self.btn_toggle = tk.Button(self.overlay_frame, text="👁 Candles", bg=COLOR_BG, fg=COLOR_TEXT_DIM,
                                 bd=0, font=("Segoe UI", 9), cursor="hand2",
                                 activebackground=COLOR_CARD, activeforeground=COLOR_ACCENT,
                                 command=self.toggle_candles)
        self.btn_toggle.pack(side=tk.LEFT)

        self.ax.tick_params(axis='x', colors=COLOR_TEXT_DIM, labelsize=8)
        self.ax.tick_params(axis='y', colors=COLOR_TEXT_DIM, labelsize=9)
        self.ax.grid(True, color=COLOR_BORDER, linestyle='-', linewidth=0.5, alpha=0.3)

        self.candles = []
        self.current_symbol = ""
        self.loaded_symbol = None
        self.last_price = 0
        self.current_interval = "1m"
        self.show_candles_flag = True
        self.active_orders = [] 

        self.is_dragging = False
        self.press_pixel_x = None; self.press_pixel_y = None
        self.press_xlim = None; self.press_ylim = None    
        self.auto_scroll = True
        self.manual_y_mode = False 
        self.background = None
        self.months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        self.collection_bars = None 
        self.collection_wicks = None
        self.price_line = None
        self.price_text = None
        
        self.cursor_line_x = self.ax.axvline(0, color=COLOR_TEXT_DIM, linestyle='--', linewidth=0.8, alpha=0, animated=True)
        self.cursor_line_y = self.ax.axhline(0, color=COLOR_TEXT_DIM, linestyle='--', linewidth=0.8, alpha=0, animated=True)
        self.tooltip = self.ax.annotate("", xy=(0, 0), xytext=(15, 15), textcoords="offset points", bbox=dict(boxstyle="round", fc=COLOR_SIDEBAR, ec=COLOR_BORDER, alpha=0.9), color=COLOR_TEXT_MAIN, fontsize=9, animated=True)
        self.tooltip.set_visible(False)

        self.highlight_tf_button("1m")

        self.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("draw_event", self.on_draw)

    def update_active_orders(self, orders_data):
        self.active_orders = orders_data
        if self.loaded_symbol:
            self._draw_all_candles(self.loaded_symbol, reset_view=False)

    def change_timeframe(self, interval):
        self.current_interval = interval
        self.highlight_tf_button(interval)
        if self.current_symbol:
            self.fetch_and_draw(self.current_symbol, interval)

    def highlight_tf_button(self, interval):
        for tf, btn in self.tf_buttons.items():
            if tf == interval:
                btn.config(fg=COLOR_ACCENT, font=("Segoe UI", 9, "bold"))
            else:
                btn.config(fg=COLOR_TEXT_DIM, font=("Segoe UI", 9))

    def fetch_and_draw(self, symbol, interval=None):
        self.current_symbol = symbol
        if interval: self.current_interval = interval
        self.lbl_symbol.config(text=f"{symbol.upper()}")
        
        self.loaded_symbol = None
        self.auto_scroll = True
        self.manual_y_mode = False 
        
        if hasattr(self, 'cursor_line_x'):
            self.cursor_line_x.set_visible(False)
            self.cursor_line_y.set_visible(False)
            self.tooltip.set_visible(False)
        
        threading.Thread(target=self._worker, args=(symbol, self.current_interval), daemon=True).start()

    def _worker(self, symbol, interval):
        data = get_kline_data(symbol, interval)
        if symbol != self.current_symbol or interval != self.current_interval: return
        if data:
            self.candles = data
            self.last_price = data[-1]['close']
            self.loaded_symbol = symbol
            self.canvas_widget.after(0, self._draw_all_candles, symbol, True)

    def _get_interval_ms(self, interval):
        unit = interval[-1]
        try: value = int(interval[:-1])
        except: return 60000
        if unit == 'm': return value * 60 * 1000
        elif unit == 'h': return value * 60 * 60 * 1000
        elif unit == 'd': return value * 24 * 60 * 60 * 1000
        elif unit == 'w': return value * 7 * 24 * 60 * 60 * 1000
        elif unit == 'M': return value * 30 * 24 * 60 * 60 * 1000
        return 60000

    def _format_date_coord(self, x, pos):
        try:
            index = int(x)
            if 0 <= index < len(self.candles):
                ts = self.candles[index]['time'] / 1000
                dt = datetime.fromtimestamp(ts)
                if self.current_interval in ['1d', '1w', '1M']:
                    return f"{dt.day} {self.months[dt.month]}"
                else:
                    return f"{dt.hour:02}:{dt.minute:02}"
            return ""
        except: return ""

    def on_draw(self, event):
        if event is not None and event.canvas == self.canvas:
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)
            self._draw_cursor_artists()

    def _draw_cursor_artists(self):
        if not hasattr(self, 'cursor_line_x'): return

        if self.cursor_line_x.get_visible():
            self.ax.draw_artist(self.cursor_line_x)
            self.ax.draw_artist(self.cursor_line_y)
            self.ax.draw_artist(self.tooltip)

    def _draw_all_candles(self, symbol, reset_view=False):
        prev_xlim = self.ax.get_xlim()
        prev_ylim = self.ax.get_ylim()

        self.ax.clear()
        self.ax.grid(True, color=COLOR_BORDER, linestyle='-', linewidth=0.5, alpha=0.3)
        self.ax.xaxis.set_major_formatter(FuncFormatter(self._format_date_coord))
        
        if self.show_candles_flag and self.candles:
            width = 0.6
            half_width = width / 2
            wick_segments = []
            bar_verts = []
            colors = []
            for i, c in enumerate(self.candles):
                open_p, close_p, low_p, high_p = c['open'], c['close'], c['low'], c['high']
                color = COLOR_UP if close_p >= open_p else COLOR_DOWN
                wick_segments.append(((i, low_p), (i, high_p)))
                rect = [(i - half_width, open_p), (i - half_width, close_p), (i + half_width, close_p), (i + half_width, open_p)]
                bar_verts.append(rect)
                colors.append(color)

            self.collection_wicks = LineCollection(wick_segments, colors=colors, linewidths=1)
            self.collection_bars = PolyCollection(bar_verts, facecolors=colors, edgecolors=colors)
            self.ax.add_collection(self.collection_wicks)
            self.ax.add_collection(self.collection_bars)
        
        trans = transforms.blended_transform_factory(self.ax.transAxes, self.ax.transData)
        for order in self.active_orders:
            line_color = COLOR_ACCENT if order['side'] == 'BUY' else COLOR_DOWN
            self.ax.axhline(order['entry'], color=line_color, linestyle='-', linewidth=1.2, alpha=0.9)
            self.ax.text(0.01, order['entry'], f"{order['side']} x{order['lot']} @ {order['entry']}", 
                         color=line_color, transform=trans, fontsize=8, va='bottom', fontweight='bold')
            
            if order.get('tp', 0) > 0:
                self.ax.axhline(order['tp'], color=COLOR_UP, linestyle='--', linewidth=1.0, alpha=0.8)
                self.ax.text(0.01, order['tp'], f"TP x{order['lot']} @ {order['tp']}", 
                             color=COLOR_UP, transform=trans, fontsize=8, va='bottom')
                
            if order.get('sl', 0) > 0:
                self.ax.axhline(order['sl'], color=COLOR_DOWN, linestyle='--', linewidth=1.0, alpha=0.8)
                self.ax.text(0.01, order['sl'], f"SL x{order['lot']} @ {order['sl']}", 
                             color=COLOR_DOWN, transform=trans, fontsize=8, va='bottom')

        last_close = self.candles[-1]['close']
        self.price_line = self.ax.axhline(last_close, color=COLOR_TEXT_DIM, linestyle='--', linewidth=1, alpha=0.8)
        
        self.price_text = self.ax.text(1.002, last_close, f"{last_close:.2f}", color='white', transform=trans, ha='left', va='center', fontsize=9, bbox=dict(facecolor=COLOR_SIDEBAR, edgecolor=COLOR_BORDER, alpha=1.0, pad=3))

        self.cursor_line_x = self.ax.axvline(0, color=COLOR_TEXT_DIM, linestyle='--', linewidth=0.8, alpha=0, animated=True)
        self.cursor_line_y = self.ax.axhline(last_close, color=COLOR_TEXT_DIM, linestyle='--', linewidth=0.8, alpha=0, animated=True)
        self.tooltip = self.ax.annotate("", xy=(0,0), xytext=(15,15), textcoords="offset points", bbox=dict(boxstyle="round", fc=COLOR_SIDEBAR, ec=COLOR_BORDER, alpha=0.9), color=COLOR_TEXT_MAIN, fontsize=9, animated=True)
        self.cursor_line_x.set_visible(False)
        self.cursor_line_y.set_visible(False)
        self.tooltip.set_visible(False)

        if reset_view:
            total_candles = len(self.candles)
            self.ax.set_xlim(total_candles - 60, total_candles + 5)
            self._update_ylim()
        else:
            self.ax.set_xlim(prev_xlim)
            self.ax.set_ylim(prev_ylim) 

        self.canvas.draw()

    def _update_ylim(self):
        if self.manual_y_mode or self.is_dragging: return
        try:
            cur_xlim = self.ax.get_xlim()
            start_idx = int(max(0, cur_xlim[0]))
            end_idx = int(min(len(self.candles), cur_xlim[1]))
            if start_idx >= end_idx: return 
            if end_idx > start_idx:
                visible_candles = self.candles[start_idx:end_idx]
                highs = [c['high'] for c in visible_candles]
                lows = [c['low'] for c in visible_candles]
                
                for order in self.active_orders:
                    highs.append(order['entry'])
                    lows.append(order['entry'])
                    if order.get('tp', 0) > 0: highs.append(order['tp'])
                    if order.get('sl', 0) > 0: lows.append(order['sl'])

                if highs and lows:
                    y_max = max(highs)
                    y_min = min(lows)
                    padding = (y_max - y_min) * 0.1
                    if padding == 0: padding = y_max * 0.01
                    self.ax.set_ylim(y_min - padding, y_max + padding)
        except: pass

    def toggle_candles(self):
        self.show_candles_flag = not self.show_candles_flag
        if self.loaded_symbol:
            self._draw_all_candles(self.loaded_symbol, reset_view=False)

    def on_scroll(self, event):
        if not event.inaxes: return
        cur_xlim = self.ax.get_xlim()
        cur_range = cur_xlim[1] - cur_xlim[0]
        xdata = event.xdata
        scale_factor = 0.8 if event.button == 'up' else 1.2
        new_range = cur_range * scale_factor
        rel_pos = (xdata - cur_xlim[0]) / cur_range
        new_min = xdata - new_range * rel_pos
        new_max = xdata + new_range * (1 - rel_pos)
        if new_range < 5 or new_range > len(self.candles) * 3: return
        self.ax.set_xlim(new_min, new_max)
        self._update_ylim()
        self.auto_scroll = (new_max >= len(self.candles) - 1)
        self.canvas.draw()

    def on_press(self, event):
        if event.button == 1 and event.inaxes:
            self.is_dragging = True
            self.press_pixel_x = event.x 
            self.press_pixel_y = event.y
            self.press_xlim = self.ax.get_xlim()
            self.press_ylim = self.ax.get_ylim()
            
            if hasattr(self, 'cursor_line_x'):
                self.cursor_line_x.set_visible(False)
                self.cursor_line_y.set_visible(False)
                self.tooltip.set_visible(False)

    def on_release(self, event):
        self.is_dragging = False
        self.press_pixel_x = None
        self.press_pixel_y = None
        if self.loaded_symbol:
            self._update_ylim() 
            self._draw_all_candles(self.loaded_symbol, reset_view=False)

    def on_hover(self, event):
        if not event.inaxes or not self.loaded_symbol: return
        
        if self.is_dragging and self.press_pixel_x is not None:
            dx_pixel = event.x - self.press_pixel_x
            dy_pixel = event.y - self.press_pixel_y
            xlim_span = self.press_xlim[1] - self.press_xlim[0]
            ylim_span = self.press_ylim[1] - self.press_ylim[0]
            bbox = self.ax.get_window_extent()
            
            dx_data = (dx_pixel / bbox.width) * xlim_span
            dy_data = (dy_pixel / bbox.height) * ylim_span
            
            new_min_x = self.press_xlim[0] - dx_data
            new_max_x = self.press_xlim[1] - dx_data
            new_min_y = self.press_ylim[0] - dy_data
            new_max_y = self.press_ylim[1] - dy_data

            self.ax.set_xlim(new_min_x, new_max_x)
            self.ax.set_ylim(new_min_y, new_max_y)
            
            if abs(dy_pixel) > 5: self.manual_y_mode = True
            if new_max_x < len(self.candles) - 2: self.auto_scroll = False
            else: self.auto_scroll = True
            
            self.canvas.draw_idle()
            return

        if self.background is None: 
            self.canvas.draw_idle()
            return

        self.canvas.restore_region(self.background)
        index = int(round(event.xdata))
        mouse_price = event.ydata
        if 0 <= index < len(self.candles):
            candle = self.candles[index]
            ts = candle['time'] / 1000
            dt = datetime.fromtimestamp(ts)
            days_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            day_str = days_en[dt.weekday()]
            month_str = self.months[dt.month]
            year_str = str(dt.year)[2:]
            date_text = f"{day_str} {dt.day} {month_str} '{year_str}\n{dt.hour:02}:{dt.minute:02}"
            
            if hasattr(self, 'cursor_line_x'):
                self.cursor_line_x.set_visible(True)
                self.cursor_line_y.set_visible(True)
                self.tooltip.set_visible(True)
                self.cursor_line_x.set_xdata([index])
                self.cursor_line_y.set_ydata([mouse_price])
                self.cursor_line_x.set_alpha(0.5)
                self.cursor_line_y.set_alpha(0.5)
                self.tooltip.xy = (index, mouse_price)
                self.tooltip.set_text(f"{date_text}\nPrice: {mouse_price:,.2f}")
                self._draw_cursor_artists()
                self.canvas.blit(self.ax.bbox)

    def update_current_price(self, price):
        if not self.candles or self.loaded_symbol is None: return
        if self.is_dragging: return 

        last_candle = self.candles[-1]
        last_time = last_candle['time']
        interval_ms = self._get_interval_ms(self.current_interval)
        next_open_time = last_time + interval_ms
        now_ts = time.time() * 1000
        
        if now_ts >= next_open_time:
            new_candle = {'time': next_open_time, 'open': price, 'high': price, 'low': price, 'close': price}
            self.candles.append(new_candle)
            if self.auto_scroll:
                cur_xlim = self.ax.get_xlim()
                self.ax.set_xlim(cur_xlim[0] + 1, cur_xlim[1] + 1)
        else:
            last_candle['close'] = price
            if price > last_candle['high']: last_candle['high'] = price
            if price < last_candle['low']: last_candle['low'] = price

        if self.auto_scroll:
            cur_xlim = self.ax.get_xlim()
            if len(self.candles) - 1 > cur_xlim[1]:
                shift = (len(self.candles) - 1) - cur_xlim[1]
                self.ax.set_xlim(cur_xlim[0] + shift, cur_xlim[1] + shift)

        if price > self.last_price: trend_color = COLOR_ACCENT
        elif price < self.last_price: trend_color = COLOR_DOWN
        else: trend_color = self.price_line.get_color() if self.price_line else COLOR_TEXT_DIM
        self.last_price = price 
        
        if self.price_line and self.price_text:
            self.price_line.set_ydata([price])
            self.price_line.set_color(trend_color)
            self.price_text.set_y(price)
            self.price_text.set_text(f"{price:.2f}")
            self.price_text.set_backgroundcolor(trend_color)
        
        self._draw_all_candles(self.loaded_symbol, reset_view=False)

    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, anchor=tk.N)

    def hide(self):
        self.frame.pack_forget()