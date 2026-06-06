from flask import Flask, request
import yfinance as yf
import plotly.graph_objects as go
import time

app = Flask(__name__)

# ---------------- CACHE (FIX RATE LIMIT) ----------------
cache = {}
CACHE_TIME = 300  # 5 minutes

def get_stock(ticker):
    now = time.time()

    if ticker in cache:
        data, timestamp = cache[ticker]
        if now - timestamp < CACHE_TIME:
            return data

    stock = yf.Ticker(ticker)

    # safe fetch (Yahoo can fail sometimes)
    try:
        info = stock.info
    except:
        info = {}

    try:
        price = stock.fast_info.get("lastPrice", 0)
    except:
        price = 0

    data = (stock, info, price)
    cache[ticker] = (data, now)

    return data

# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    result = ""

    if request.method == "POST":

        ticker = request.form["ticker"].upper()

        try:
            stock, info, price = get_stock(ticker)

            # ---------------- SAFE DATA HANDLING ----------------
            company = info.get("longName") or info.get("shortName") or ticker
            sector = info.get("sector") or "Unknown"
            industry = info.get("industry") or "N/A"
            country = info.get("country") or "N/A"

            # ---------------- CHARTS ----------------
            hist_1m = stock.history(period="1mo")
            hist_6m = stock.history(period="6mo")

            fig1 = go.Figure()
            if not hist_1m.empty:
                fig1.add_trace(go.Scatter(x=hist_1m.index, y=hist_1m["Close"], name="1M"))
            fig1.update_layout(template="plotly_dark", height=300)
            chart1 = fig1.to_html(full_html=False)

            fig2 = go.Figure()
            if not hist_6m.empty:
                fig2.add_trace(go.Scatter(x=hist_6m.index, y=hist_6m["Close"], name="6M"))
            fig2.update_layout(template="plotly_dark", height=300)
            chart2 = fig2.to_html(full_html=False)

            # ---------------- RESULT UI ----------------
            result = f"""
            <div class="card">
                <h2>{company}</h2>
                <h3>{ticker}</h3>

                <h2>💰 Price: ${price}</h2>

                <hr>

                <p><b>Sector:</b> {sector}</p>
                <p><b>Industry:</b> {industry}</p>
                <p><b>Country:</b> {country}</p>

                <hr>

                <h3>📈 1 Month Chart</h3>
                {chart1}

                <h3>📊 6 Month Chart</h3>
                {chart2}
            </div>
            """

        except Exception as e:
            result = f"<div class='card'>Error: {e}</div>"

    return f"""
<!DOCTYPE html>
<html>
<head>
<title>Stock App Pro</title>

<style>
body {{
    margin: 0;
    font-family: Arial;
    background: #0b1220;
    color: white;
    text-align: center;
}}

.container {{
    width: 900px;
    margin: auto;
    padding: 20px;
}}

.card {{
    background: #1e293b;
    padding: 20px;
    margin-top: 20px;
    border-radius: 12px;
    text-align: left;
}}

input {{
    padding: 10px;
    margin: 5px;
    border-radius: 8px;
    border: none;
}}

button {{
    padding: 10px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
}}
</style>

</head>

<body>

<div class="container">

<h1>🚀 STOCK APP PRO (STABLE)</h1>

<form method="POST">
    <input name="ticker" placeholder="NVDA, TSLA, AAPL, BTC-USD">
    <button type="submit">Search</button>
</form>

{result}

</div>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
