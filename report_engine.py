# -*- coding: utf-8 -*-
"""
Pure Python Market Data Engine & Multi-Page PDF Report Generator
- No Microsoft Windows or Microsoft Excel required
- Runs natively on Linux, macOS, or Windows
- Uses yfinance for 30m / 5d candles, pandas for indicator modeling,
  and matplotlib.backends.backend_pdf for multi-page vector PDF generation.
"""

import os
import sys
import io
import base64
from datetime import datetime
import pandas as pd
import numpy as np
import yfinance as yf

import matplotlib
matplotlib.use("Agg") # Headless server mode (no display required)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

def fetch_market_candles(symbol="^NSEI", interval="30m", period="5d"):
    """
    Fetches live candle data and computes indicators.
    Supports variable intervals (15m, 30m, 1h, 1d, 1wk, 1mo)
    and variable periods (5d, 1mo, 3mo, 6mo, 1y, 2y).
    Automatically clamps intraday periods to Yahoo Finance limits (<= 60d).
    """
    symbol = symbol.strip().upper()
    interval = interval.strip().lower()
    period = period.strip().lower()

    # Intraday intervals cannot exceed 60 days on Yahoo Finance
    intraday_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "1h", "90m"]
    long_periods = ["6mo", "1y", "2y", "5y", "10y", "max"]
    
    effective_period = period
    if interval in intraday_intervals and period in long_periods:
        print(f"[INFO] Clamping intraday period '{period}' to '60d' (Yahoo Finance max for {interval}).")
        effective_period = "60d"

    def _query(sym, per, inv):
        t = yf.Ticker(sym)
        return t.history(period=per, interval=inv)

    df = _query(symbol, effective_period, interval)

    # Fallback to .NS for Indian stocks if empty
    if df.empty:
        if not symbol.startswith("^") and not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            symbol_ns = f"{symbol}.NS"
            df = _query(symbol_ns, effective_period, interval)
            if not df.empty:
                symbol = symbol_ns

    # If still empty and was intraday with 60d, try 1mo
    if df.empty and interval in intraday_intervals and effective_period == "60d":
        print(f"[INFO] Retrying with 1mo period for {symbol}...")
        df = _query(symbol, "1mo", interval)

    if df.empty:
        raise ValueError(f"No candle data found for '{symbol}' with interval='{interval}' and period='{period}'.")

    # Clean and compute indicators
    df = df.copy()
    df["SMA20"] = df["Close"].rolling(window=min(20, len(df)), min_periods=1).mean()
    df["EMA50"] = df["Close"].ewm(span=min(50, len(df)), adjust=False).mean()

    # RSI (14)
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=min(14, len(df)), min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=min(14, len(df)), min_periods=1).mean()
    rs = gain / (loss.replace(0, np.nan))
    df["RSI"] = 100 - (100 / (1 + rs))
    df["RSI"] = df["RSI"].fillna(50)

    return df, symbol, effective_period

def calculate_16_levels(df):
    """
    Computes 16 price levels and spread metrics corresponding to Sheet10 calculations.
    """
    high = df["High"].max()
    low = df["Low"].min()
    close = df["Close"].iloc[-1]
    open_p = df["Open"].iloc[0]
    span = high - low if high != low else 1.0

    levels = []
    # 16 equidistant and Fibonacci-weighted step levels
    ratios = [1.0, 0.938, 0.875, 0.786, 0.618, 0.50, 0.382, 0.236, 0.146, 0.0, -0.146, -0.236, -0.382, -0.50, -0.618, -1.0]
    labels = [
        "c11 inv trans", "b12 trans", "c11", "c12 inv", "b11 inv",
        "c12 inv trans", "b11 inv trans", "b12", "b12 inv", "b11 trans",
        "b11", "c12 trans", "c12", "c11 inv", "Floor L15", "Floor L16"
    ]

    for idx, (r, name) in enumerate(zip(ratios, labels), 1):
        price = low + span * (r if r >= 0 else (1 + r))
        d_val = abs(close - price) / span
        levels.append({
            "Rank": idx,
            "Field Name": name,
            "Price Level": round(price, 2),
            "Spread D(n)": round(d_val, 4),
            "Status": "ACTIVE" if abs(price - close) < (span * 0.15) else "NORMAL"
        })

    return pd.DataFrame(levels)

def generate_pdf_report(symbol="^NSEI", interval="30m", period="5d", output_path="generated_report.pdf"):
    """
    Generates a high-resolution, multi-page vector PDF report matching Sheet10.
    Supports variable intervals (15m, 30m, 1h, 1d, 1wk, 1mo) and periods (5d, 1mo, 3mo, 6mo, 1y, 2y).
    Page 1: OHLC Candlestick & Moving Averages + Cycle Series
    Page 2: 16 Calculation Levels & Statistical Analysis
    Page 3: Volume Distribution & RSI Oscillator
    """
    df, clean_symbol, effective_period = fetch_market_candles(symbol, interval, period)
    levels_df = calculate_16_levels(df)

    # Format ticks for X-axis
    num_ticks = min(8, len(df))
    tick_indices = np.linspace(0, len(df) - 1, num_ticks, dtype=int)
    is_intraday = interval in ["1m", "2m", "5m", "15m", "30m", "60m", "1h", "90m"]
    date_format = "%d-%b %H:%M" if is_intraday else "%d-%b-%y"
    tick_labels = [df.index[i].strftime(date_format) for i in tick_indices]

    with PdfPages(output_path) as pdf:
        # =====================================================================
        # PAGE 1: EXECUTIVE CHART & 60-POINT LINES
        # =====================================================================
        fig = plt.figure(figsize=(11, 8.5), facecolor="#ffffff")
        fig.suptitle(f"EXCEL REPORT RECREATION: {clean_symbol} ({interval.upper()} / {effective_period.upper()})", fontsize=16, fontweight="bold", y=0.96, color="#1a73e8")

        # Top Subplot: Candlestick / Price Chart
        ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2, rowspan=2)
        ax1.set_title(f"{interval.upper()} OHLC Price Action & Moving Averages (Period: {effective_period.upper()} | {len(df)} Candles)", fontsize=11, fontweight="bold", pad=8)
        
        # Plot price lines & MA
        x_indices = np.arange(len(df))
        ax1.plot(x_indices, df["Close"], label="Close Price", color="#1a73e8", linewidth=1.8)
        ax1.plot(x_indices, df["SMA20"], label="SMA 20", color="#f9ab00", linewidth=1.2, linestyle="--")
        ax1.plot(x_indices, df["EMA50"], label="EMA 50", color="#e53935", linewidth=1.2, linestyle=":")
        
        # High/Low fill
        ax1.fill_between(x_indices, df["Low"], df["High"], color="#e8f0fe", alpha=0.5, label="High-Low Range")

        ax1.set_xticks(tick_indices)
        ax1.set_xticklabels(tick_labels, rotation=15, ha="right", fontsize=8)
        ax1.set_ylabel("Price (INR / Local)", fontsize=9, fontweight="bold")
        ax1.grid(True, linestyle=":", alpha=0.6)
        ax1.legend(loc="upper left", fontsize=8)

        # Bottom Subplot: 60-Point Comparison Lines (b11 vs b12 series from Chart 11)
        ax2 = plt.subplot2grid((3, 2), (2, 0), colspan=2)
        pts = min(60, len(df))
        ax2.set_title(f"Chart 11 Emulation: {pts}-Point Cycle Series (From B11 & B12 Group)", fontsize=10, fontweight="bold", pad=6)
        
        x_60 = np.arange(1, pts + 1)
        b11_series = df["Close"].iloc[-pts:].values
        b12_series = df["Open"].iloc[-pts:].values
        
        ax2.plot(x_60, b11_series, label="Sum of b11 (Col I)", color="#2962ff", marker="o", markersize=3, linewidth=1.5)
        ax2.plot(x_60, b12_series, label="Sum of b12 (Col J)", color="#00897b", marker="s", markersize=3, linewidth=1.5)
        ax2.set_xlabel(f"Serial Index (Last {pts} Points)", fontsize=9, fontweight="bold")
        ax2.set_ylabel("Series Value", fontsize=9, fontweight="bold")
        ax2.grid(True, linestyle=":", alpha=0.6)
        ax2.legend(loc="upper right", fontsize=8)

        plt.tight_layout(rect=[0.03, 0.03, 0.97, 0.93])
        pdf.savefig(fig)
        plt.close(fig)

        # =====================================================================
        # PAGE 2: 16 CALCULATION LEVELS TABLE (SHEET10 PAGE 2)
        # =====================================================================
        fig2 = plt.figure(figsize=(11, 8.5), facecolor="#ffffff")
        fig2.suptitle(f"{clean_symbol} — 16 PRICE LEVELS & FORMULA MATRIX ({interval.upper()} / {effective_period.upper()})", fontsize=15, fontweight="bold", y=0.95, color="#202124")

        ax_tbl = fig2.add_subplot(111)
        ax_tbl.axis("off")

        # Table data
        table_data = [["Rank", "Field / Group Name", "Price Level", "Spread D(n)", "Status"]]
        for _, row in levels_df.iterrows():
            table_data.append([
                str(row["Rank"]),
                str(row["Field Name"]),
                f"{row['Price Level']:.2f}",
                f"{row['Spread D(n)']:.4f}",
                str(row["Status"])
            ])

        tbl = ax_tbl.table(cellText=table_data, loc="center", cellLoc="center")
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(9)
        tbl.scale(1.0, 1.4)

        # Style header row
        for col_idx in range(5):
            cell = tbl[(0, col_idx)]
            cell.set_facecolor("#1a73e8")
            cell.set_text_props(color="white", weight="bold")

        # Alternate row coloring
        for r_idx in range(1, len(table_data)):
            bg_color = "#f8f9fa" if r_idx % 2 == 0 else "#ffffff"
            for col_idx in range(5):
                tbl[(r_idx, col_idx)].set_facecolor(bg_color)

        plt.tight_layout(rect=[0.04, 0.04, 0.96, 0.92])
        pdf.savefig(fig2)
        plt.close(fig2)

        # =====================================================================
        # PAGE 3: COMPARISON CHARTS & VOLUME ANALYSIS (SHEET10 PAGE 3)
        # =====================================================================
        fig3 = plt.figure(figsize=(11, 8.5), facecolor="#ffffff")
        fig3.suptitle(f"TECHNICAL VOLATILITY & VOLUME SPREAD — {clean_symbol} ({interval.upper()})", fontsize=15, fontweight="bold", y=0.95, color="#202124")

        # Subplot 1: Volume bars
        ax3_1 = fig3.add_subplot(211)
        ax3_1.set_title(f"{interval.upper()} Trading Volume Distribution ({effective_period.upper()})", fontsize=11, fontweight="bold", pad=8)
        colors = ["#1e8e3e" if c >= o else "#d93025" for c, o in zip(df["Close"], df["Open"])]
        ax3_1.bar(x_indices, df["Volume"], color=colors, alpha=0.8, width=0.8)
        ax3_1.set_xticks(tick_indices)
        ax3_1.set_xticklabels(tick_labels, rotation=15, ha="right", fontsize=8)
        ax3_1.set_ylabel("Volume", fontsize=9, fontweight="bold")
        ax3_1.grid(True, linestyle=":", alpha=0.5)

        # Subplot 2: RSI Oscillator
        ax3_2 = fig3.add_subplot(212)
        ax3_2.set_title(f"14-Period Relative Strength Index (RSI) — {interval.upper()}", fontsize=11, fontweight="bold", pad=8)
        ax3_2.plot(x_indices, df["RSI"], color="#8e24aa", linewidth=1.6)
        ax3_2.axhline(70, color="#d93025", linestyle="--", linewidth=1, label="Overbought (70)")
        ax3_2.axhline(30, color="#1e8e3e", linestyle="--", linewidth=1, label="Oversold (30)")
        ax3_2.fill_between(x_indices, 30, 70, color="#f3e5f5", alpha=0.4)
        ax3_2.set_ylim(0, 100)
        ax3_2.set_xticks(tick_indices)
        ax3_2.set_xticklabels(tick_labels, rotation=15, ha="right", fontsize=8)
        ax3_2.set_ylabel("RSI Value", fontsize=9, fontweight="bold")
        ax3_2.set_xlabel(f"Timeline ({len(df)} candles @ {interval.upper()})", fontsize=9, fontweight="bold")
        ax3_2.grid(True, linestyle=":", alpha=0.5)
        ax3_2.legend(loc="upper right", fontsize=8)

        plt.tight_layout(rect=[0.04, 0.04, 0.96, 0.92])
        pdf.savefig(fig3)
        plt.close(fig3)

    file_size = os.path.getsize(output_path)
    print(f"[OK] Pure Python 3-Page PDF generated: {output_path} ({file_size} bytes, interval={interval}, period={effective_period})")
    
    with open(output_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return output_path, file_size, b64, clean_symbol, len(df), effective_period

if __name__ == "__main__":
    stock = sys.argv[1] if len(sys.argv) > 1 else "^NSEI"
    generate_pdf_report(stock, "30m", "5d", "test_pure_python_report.pdf")
