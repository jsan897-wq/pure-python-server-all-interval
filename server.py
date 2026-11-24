# -*- coding: utf-8 -*-
"""
Pure Python Market Report Server & API
Runs on Linux, Windows, macOS, or in Docker on Render / Cloud Run / Railway.
Zero Microsoft Windows or Microsoft Excel dependencies.
"""

import os
import sys
import requests
from flask import Flask, request, jsonify, send_file, render_template_string
from report_engine import generate_pdf_report

app = Flask(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LATEST_PDF_PATH = os.path.join(CURRENT_DIR, "latest_report.pdf")
DOCS_HTML_PATH = os.path.join(CURRENT_DIR, "documentation.html")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pure Python Market Report Server</title>
  <style>
    :root {
      --primary: #1a73e8;
      --bg: #f8f9fa;
      --card-bg: #ffffff;
      --text: #202124;
      --border: #dadce0;
      --success: #1e8e3e;
      --success-bg: #e6f4ea;
      --warning: #f9ab00;
      --warning-bg: #fef7e0;
      --error: #d93025;
      --error-bg: #fce8e6;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 30px 16px;
      display: flex;
      justify-content: center;
    }
    .container {
      width: 100%;
      max-width: 680px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 28px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }
    h1 {
      font-size: 22px;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      background: #e6f4ea;
      color: var(--success);
    }
    p.subtitle {
      color: #5f6368;
      font-size: 14px;
      line-height: 1.5;
      margin-top: 4px;
      margin-bottom: 20px;
    }
    .box-card {
      background: #f8f9fa;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 18px;
    }
    .form-group {
      margin-bottom: 14px;
    }
    label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      color: #3c4043;
      margin-bottom: 6px;
    }
    .input-row {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
    }
    .search-input, .add-input, .select-stock {
      flex: 1;
      padding: 11px 14px;
      font-size: 14px;
      border: 1.5px solid var(--border);
      border-radius: 8px;
      background: #ffffff;
      color: var(--text);
      outline: none;
      box-sizing: border-box;
      transition: border-color 0.2s;
    }
    .search-input:focus, .add-input:focus, .select-stock:focus {
      border-color: var(--primary);
    }
    .btn-action {
      padding: 11px 18px;
      font-size: 14px;
      font-weight: 600;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: background 0.2s;
      white-space: nowrap;
    }
    .btn-search {
      background: var(--primary);
      color: white;
    }
    .btn-search:hover {
      background: #1557b0;
    }
    .btn-add {
      background: #1e8e3e;
      color: white;
    }
    .btn-add:hover {
      background: #137333;
    }
    .btn-reset {
      background: #dadce0;
      color: #3c4043;
    }
    .btn-reset:hover {
      background: #bdc1c6;
    }
    .search-feedback {
      font-size: 12px;
      color: #5f6368;
      margin-top: 4px;
    }
    .info-tags {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
    }
    .tag {
      background: #f1f3f4;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      color: #3c4043;
    }
    .btn-run {
      background: var(--primary);
      color: white;
      border: none;
      padding: 14px 24px;
      font-size: 16px;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
      width: 100%;
      box-sizing: border-box;
      transition: background 0.2s;
    }
    .btn-run:hover {
      background: #1557b0;
    }
    .btn-run:disabled {
      background: #dadce0;
      cursor: not-allowed;
    }
    .status-box {
      margin-top: 22px;
      padding: 18px;
      border-radius: 10px;
      font-size: 14px;
      display: none;
    }
    .status-running {
      background: var(--warning-bg);
      color: #8c5300;
      border: 1px solid var(--warning);
    }
    .status-completed {
      background: var(--success-bg);
      color: #137333;
      border: 1px solid #34a853;
    }
    .status-failed {
      background: var(--error-bg);
      color: var(--error);
      border: 1px solid var(--error);
    }
    .button-group {
      display: flex;
      gap: 10px;
      margin-top: 16px;
      flex-wrap: wrap;
    }
    .download-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #1e8e3e;
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 600;
      font-size: 14px;
      transition: background 0.2s;
      flex: 1;
      justify-content: center;
    }
    .download-btn:hover {
      background: #137333;
    }
    .preview-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #ffffff;
      color: var(--primary);
      border: 1.5px solid var(--primary);
      padding: 12px 20px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 600;
      font-size: 14px;
      transition: background 0.2s;
      flex: 1;
      justify-content: center;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🐍 Pure Python Market Server</h1>
      <div style="display:flex; align-items:center; gap:10px;">
        <a href="/docs" target="_blank" style="font-size:13px; font-weight:600; color:var(--primary); text-decoration:none;">📖 Documentation</a>
        <span class="badge">100% Linux Native</span>
      </div>
    </div>
    <p class="subtitle">Runs on any free Linux cloud server or locally without requiring Windows or Microsoft Excel desktop.</p>

    <!-- Search & Stock Controls Card -->
    <div class="box-card">
      <!-- 1. Search Stock Input with Search Button -->
      <div class="form-group">
        <label for="searchInput">🔍 Search Stocks / Filter Dropdown:</label>
        <div class="input-row">
          <input type="text" id="searchInput" class="search-input" placeholder="Type name or symbol (e.g. Tata, Adani, Bank, Reliance, ITC)..." onkeyup="if(event.key==='Enter') searchStocks()">
          <button type="button" class="btn-action btn-search" onclick="searchStocks()">🔍 Search</button>
          <button type="button" class="btn-action btn-reset" onclick="resetSearch()" title="Show All Stocks">↺ Reset</button>
        </div>
        <div id="searchFeedback" class="search-feedback">Showing all stocks in list.</div>
      </div>

      <!-- 2. Stock Selection Dropdown -->
      <div class="form-group" style="margin-top: 14px;">
        <label for="stockSelect">Select Stock / Index from Dropdown:</label>
        <select id="stockSelect" class="select-stock"></select>
      </div>

      <!-- 3. Add Custom Stock to Dropdown -->
      <div class="form-group" style="margin-top: 14px; margin-bottom: 0;">
        <label for="addStockInput">➕ Add New Stock to Dropdown:</label>
        <div class="input-row">
          <input type="text" id="addStockInput" class="add-input" placeholder="e.g. ZOMATO, PAYTM, WIPRO, MARUTI, AAPL..." onkeyup="if(event.key==='Enter') addNewStock()">
          <button type="button" class="btn-action btn-add" onclick="addNewStock()">➕ Add Stock</button>
        </div>
      </div>
    </div>

    <!-- Timeframe & Lookback Period Controls Card -->
    <div class="box-card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
        <label style="margin-bottom:0;">⏱ Time Interval & Lookback Period:</label>
        <span style="font-size:11px; font-weight:700; color:var(--primary); background:#e8f0fe; padding:2px 8px; border-radius:12px;">Multi-Timeframe Prediction</span>
      </div>
      
      <div style="display: flex; gap: 12px; flex-wrap: wrap;">
        <!-- Candle Interval -->
        <div style="flex: 1; min-width: 200px;">
          <label for="intervalSelect" style="font-size:12px; color:#5f6368;">Candle Interval:</label>
          <select id="intervalSelect" class="select-stock" onchange="updateTimeframeTags()">
            <option value="15m">15 Minutes (15m)</option>
            <option value="30m" selected>30 Minutes (30m - Default)</option>
            <option value="1h">1 Hour (1h)</option>
            <option value="1d">1 Day (Daily - 1d)</option>
            <option value="1wk">1 Week (Weekly - 1wk)</option>
            <option value="1mo">1 Month (Monthly - 1mo)</option>
          </select>
        </div>

        <!-- History Period -->
        <div style="flex: 1; min-width: 200px;">
          <label for="periodSelect" style="font-size:12px; color:#5f6368;">Lookback Period:</label>
          <select id="periodSelect" class="select-stock" onchange="updateTimeframeTags()">
            <option value="5d" selected>Last 5 Days (Intraday Default)</option>
            <option value="1mo">Last 1 Month</option>
            <option value="3mo">Last 3 Months</option>
            <option value="6mo">Last 6 Months</option>
            <option value="1y">Last 1 Year (Annual)</option>
            <option value="2y">Last 2 Years (Multi-Year)</option>
          </select>
        </div>
      </div>
      <div id="timeframeNote" style="font-size:11px; color:#70757a; margin-top:8px; line-height:1.4;">
        💡 <em>Intraday intervals (15m, 30m, 1h) provide up to 60 days of data. Daily (1d), Weekly, and Monthly intervals provide multi-year data.</em>
      </div>
    </div>

    <div class="info-tags">
      <span class="tag" id="tagInterval">⏱ <strong>30-Min Interval</strong></span>
      <span class="tag" id="tagPeriod">📅 <strong>Last 5 Days</strong></span>
      <span class="tag">📄 <strong>3-Page Vector PDF Report</strong></span>
    </div>

    <button id="triggerBtn" class="btn-run" onclick="generateReport()">▶ Generate Pure Python Report</button>

    <div id="statusBox" class="status-box">
      <div id="statusText">Waiting...</div>
      <div id="downloadArea"></div>
    </div>
  </div>

  <script>
    const DEFAULT_STOCKS = [
      { symbol: "^NSEI", name: "NIFTY 50 Index", group: "Indices" },
      { symbol: "^NSEBANK", name: "BANK NIFTY Index", group: "Indices" },
      { symbol: "^CNXFIN", name: "NIFTY Financial Services", group: "Indices" },
      { symbol: "^CNXIT", name: "NIFTY IT Index", group: "Indices" },
      { symbol: "^BSESN", name: "SENSEX Index", group: "Indices" },

      { symbol: "RELIANCE.NS", name: "Reliance Industries", group: "Top Stocks" },
      { symbol: "TCS.NS", name: "Tata Consultancy Services (TCS)", group: "Top Stocks" },
      { symbol: "HDFCBANK.NS", name: "HDFC Bank", group: "Top Stocks" },
      { symbol: "INFY.NS", name: "Infosys", group: "Top Stocks" },
      { symbol: "ICICIBANK.NS", name: "ICICI Bank", group: "Top Stocks" },
      { symbol: "SBIN.NS", name: "State Bank of India (SBI)", group: "Top Stocks" },
      { symbol: "TATAMOTORS.NS", name: "Tata Motors", group: "Top Stocks" },
      { symbol: "ITC.NS", name: "ITC Limited", group: "Top Stocks" },
      { symbol: "BHARTIARTL.NS", name: "Bharti Airtel", group: "Top Stocks" },
      { symbol: "LT.NS", name: "Larsen & Toubro", group: "Top Stocks" },
      { symbol: "KOTAKBANK.NS", name: "Kotak Mahindra Bank", group: "Top Stocks" },
      { symbol: "AXISBANK.NS", name: "Axis Bank", group: "Top Stocks" },
      { symbol: "BAJFINANCE.NS", name: "Bajaj Finance", group: "Top Stocks" },
      { symbol: "MARUTI.NS", name: "Maruti Suzuki", group: "Top Stocks" },
      { symbol: "HINDUNILVR.NS", name: "Hindustan Unilever", group: "Top Stocks" },
      { symbol: "SUNPHARMA.NS", name: "Sun Pharmaceutical", group: "Top Stocks" },
      { symbol: "TATASTEEL.NS", name: "Tata Steel", group: "Top Stocks" },
      { symbol: "TITAN.NS", name: "Titan Company", group: "Top Stocks" },
      { symbol: "ADANIENT.NS", name: "Adani Enterprises", group: "Top Stocks" },
      { symbol: "ADANIPORTS.NS", name: "Adani Ports", group: "Top Stocks" },
      { symbol: "WIPRO.NS", name: "Wipro", group: "Top Stocks" },
      { symbol: "ASIANPAINT.NS", name: "Asian Paints", group: "Top Stocks" },
      { symbol: "NTPC.NS", name: "NTPC Limited", group: "Top Stocks" },
      { symbol: "POWERGRID.NS", name: "Power Grid Corp", group: "Top Stocks" }
    ];

    function getStoredStocks() {
      try {
        const stored = localStorage.getItem("custom_user_stocks_py");
        return stored ? JSON.parse(stored) : [];
      } catch (e) {
        return [];
      }
    }

    function getAllStocks() {
      const custom = getStoredStocks();
      const combined = [...DEFAULT_STOCKS];
      for (const c of custom) {
        if (!combined.some(s => s.symbol.toUpperCase() === c.symbol.toUpperCase())) {
          combined.push(c);
        }
      }
      return combined;
    }

    function renderDropdown(stocksToDisplay, selectedVal = null) {
      const select = document.getElementById("stockSelect");
      const currentVal = selectedVal || select.value || "^NSEI";
      select.innerHTML = "";

      const groups = {};
      for (const item of stocksToDisplay) {
        const grp = item.group || "Custom Stocks";
        if (!groups[grp]) groups[grp] = [];
        groups[grp].push(item);
      }

      for (const [grpName, items] of Object.entries(groups)) {
        const optgroup = document.createElement("optgroup");
        optgroup.label = grpName;
        for (const it of items) {
          const opt = document.createElement("option");
          opt.value = it.symbol;
          opt.textContent = `${it.symbol} — ${it.name}`;
          if (it.symbol.toUpperCase() === currentVal.toUpperCase()) {
            opt.selected = true;
          }
          optgroup.appendChild(opt);
        }
        select.appendChild(optgroup);
      }
    }

    // Populate initially
    renderDropdown(getAllStocks());

    // Search function with Search Button
    function searchStocks() {
      const query = document.getElementById("searchInput").value.trim().toLowerCase();
      const feedback = document.getElementById("searchFeedback");
      const all = getAllStocks();

      if (!query) {
        renderDropdown(all);
        feedback.innerText = `Showing all ${all.length} stocks.`;
        return;
      }

      const filtered = all.filter(s => 
        s.symbol.toLowerCase().includes(query) || 
        s.name.toLowerCase().includes(query)
      );

      if (filtered.length > 0) {
        renderDropdown(filtered, filtered[0].symbol);
        feedback.innerHTML = `Found <strong>${filtered.length}</strong> matching stock(s).`;
      } else {
        feedback.innerHTML = `No stocks found for "<strong>${query}</strong>". You can add it below!`;
        document.getElementById("addStockInput").value = query.toUpperCase();
      }
    }

    function resetSearch() {
      document.getElementById("searchInput").value = "";
      const all = getAllStocks();
      renderDropdown(all);
      document.getElementById("searchFeedback").innerText = `Showing all ${all.length} stocks.`;
    }

    // Add stock to dropdown function
    function addNewStock() {
      const addInput = document.getElementById("addStockInput");
      let rawSymbol = addInput.value.trim().toUpperCase();

      if (!rawSymbol) {
        alert("Please enter a stock symbol (e.g. ZOMATO or MARUTI.NS).");
        return;
      }

      let finalSymbol = rawSymbol;
      if (!finalSymbol.startsWith("^") && !finalSymbol.includes(".")) {
        finalSymbol = `${finalSymbol}.NS`;
      }

      const all = getAllStocks();
      if (all.some(s => s.symbol.toUpperCase() === finalSymbol)) {
        alert(`Stock '${finalSymbol}' is already in your dropdown!`);
        renderDropdown(all, finalSymbol);
        addInput.value = "";
        return;
      }

      const newStock = {
        symbol: finalSymbol,
        name: `${rawSymbol} (User Added)`,
        group: "⭐ My Added Stocks"
      };

      const customList = getStoredStocks();
      customList.push(newStock);
      localStorage.setItem("custom_user_stocks_py", JSON.stringify(customList));

      const updatedAll = getAllStocks();
      renderDropdown(updatedAll, finalSymbol);

      addInput.value = "";
      document.getElementById("searchFeedback").innerHTML = `✅ Successfully added <strong>${finalSymbol}</strong> to dropdown!`;
    }

    function updateTimeframeTags() {
      const inv = document.getElementById("intervalSelect").value;
      const per = document.getElementById("periodSelect").value;

      const invNames = {
        "15m": "15-Min", "30m": "30-Min", "1h": "1-Hour",
        "1d": "Daily (1d)", "1wk": "Weekly (1wk)", "1mo": "Monthly (1mo)"
      };
      const perNames = {
        "5d": "Last 5 Days", "1mo": "Last 1 Month", "3mo": "Last 3 Months",
        "6mo": "Last 6 Months", "1y": "Last 1 Year", "2y": "Last 2 Years"
      };

      document.getElementById("tagInterval").innerHTML = `⏱ <strong>${invNames[inv] || inv}</strong>`;
      document.getElementById("tagPeriod").innerHTML = `📅 <strong>${perNames[per] || per}</strong>`;

      const note = document.getElementById("timeframeNote");
      const isIntraday = ["15m", "30m", "1h"].includes(inv);
      const isLong = ["6mo", "1y", "2y"].includes(per);
      if (isIntraday && isLong) {
        note.innerHTML = `⚠️ <em>Intraday data for ${inv} is limited to ~60 days by Yahoo Finance. The engine will automatically fetch the maximum 60-day intraday window.</em>`;
        note.style.color = "#d93025";
      } else {
        note.innerHTML = `💡 <em>Intraday intervals (15m, 30m, 1h) provide up to 60 days of data. Daily (1d), Weekly, and Monthly intervals provide multi-year data.</em>`;
        note.style.color = "#70757a";
      }
    }

    async function generateReport() {
      const select = document.getElementById("stockSelect");
      const symbol = select.value || "^NSEI";
      const interval = document.getElementById("intervalSelect").value;
      const period = document.getElementById("periodSelect").value;

      const btn = document.getElementById("triggerBtn");
      const statusBox = document.getElementById("statusBox");
      const statusText = document.getElementById("statusText");
      const downloadArea = document.getElementById("downloadArea");

      btn.disabled = true;
      btn.innerText = `⏳ Generating report for ${symbol} (${interval} / ${period})...`;
      statusBox.style.display = "block";
      statusBox.className = "status-box status-running";
      statusText.innerHTML = `<strong>Status:</strong> Fetching ${interval} candles (${period}) and generating 3-page charts for <strong>${symbol}</strong>...`;
      downloadArea.innerHTML = "";

      try {
        const res = await fetch("/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ stock: symbol, interval: interval, period: period })
        });
        const data = await res.json();

        if (!data.success) throw new Error(data.error || "Generation failed");

        btn.disabled = false;
        btn.innerText = "▶ Generate Pure Python Report";
        statusBox.className = "status-box status-completed";
        statusText.innerHTML = `<strong>Status:</strong> ✅ <strong>${data.stock}</strong> (${data.interval} / ${data.period}) report with <strong>${data.candles} candles</strong> generated in ${(data.duration || 2.5).toFixed(1)}s! (${(data.size / 1024).toFixed(1)} KB)`;

        downloadArea.innerHTML = `
          <div class="button-group">
            <a class="download-btn" href="/api/download" download="${data.stock}_${data.interval}_${data.period}_Report.pdf">
              ⬇ Download Generated PDF (${(data.size / 1024).toFixed(1)} KB)
            </a>
            <a class="preview-btn" href="/api/download" target="_blank">
              👁 Preview in Browser
            </a>
          </div>
        `;
      } catch (err) {
        btn.disabled = false;
        btn.innerText = "▶ Generate Pure Python Report";
        statusBox.className = "status-box status-failed";
        statusText.innerHTML = `<strong>Error:</strong> ${err.message}`;
      }
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/docs")
def docs():
    if os.path.exists(DOCS_HTML_PATH):
        return send_file(DOCS_HTML_PATH)
    return "Documentation file not found.", 404

@app.route("/api/generate", methods=["POST"])
def api_generate():
    import time
    start = time.time()
    data = request.get_json() or {}
    stock = data.get("stock", "^NSEI")
    interval = data.get("interval", "30m")
    period = data.get("period", "5d")

    try:
        pdf_path, size, b64, clean_sym, count, effective_period = generate_pdf_report(
            stock, interval=interval, period=period, output_path=LATEST_PDF_PATH
        )
        duration = time.time() - start
        return jsonify({
            "success": True,
            "stock": clean_sym,
            "interval": interval,
            "period": effective_period,
            "size": size,
            "candles": count,
            "duration": duration
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/download")
def api_download():
    if os.path.exists(LATEST_PDF_PATH):
        return send_file(LATEST_PDF_PATH, mimetype="application/pdf", as_attachment=False)
    return "No report generated yet.", 404

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "Pure Python Market Report Server"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("=" * 60)
    print(f"  [PURE PYTHON SERVER] Running on http://localhost:{port}")
    print("  Zero Windows / Zero Excel required!")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
