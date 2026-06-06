from flask import Flask, request
import yfinance as yf
import plotly.graph_objects as go
import requests
import os

app = Flask(__name__)

# ---------------- SECURE API KEY ----------------
FMP_API_KEY = os.getenv("FMP_API_KEY")

# ---------------- GET PRICE ----------------
def get_price(ticker):
    stock = yf.Ticker(ticker)
    try:
        price = stock.fast_info.get("lastPrice", 0)
    except:
        price = 0
    return price, stock

# ---------------- REAL COMPANY DATA ----------------
def get_company_data(ticker):

    if not FMP_API_KEY:
        return {}

    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"

    try:
        r = requests.get(url, timeout=5)
        data = r.json()

        if isinstance(data, list) and len(data) > 0:
            return data[0]

    except:
        pass

    return {}

# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    result = ""

    if request.method == "POST":

        ticker = request.form["ticker"].upper()

        try:
            price, stock = get_price(ticker)
            info = get_company_data(ticker)

            company = info.get("companyName") or ticker
            sector = info.get("sector") or "Unknown"
            industry = info.get("industry") or "N/A"
            country = info.get("country") or "N/A"
            market_cap = info.get("mktCap") or "N/A"

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

            # ---------------- UI ----------------
            result = f"""
            <div class="card">
                <h2>🚀 {company}</h2>
                <h3>{ticker}</h3>

                <h2>💰 Price: ${price}</h2>

                <hr>

                <p><b>Sector:</b> {sector}</p>
                <p><b>Industry:</b> {industry}</p>
                <p><b>Country:</b> {country}</p>
                <p><b>Market Cap:</b> {market_cap}</p>

                <hr>

                <h3>📈 1 Month Chart</h3>
                {chart1}

                <h3>📊 6 Month Chart</h3>
                {chart2}
            </div>
            """

        except Exception as e:
            result = f"<div style='color:red;'>Error: {e}</div>"

    return f"""
<!DOCTYPE html>
<html>
<head>
<title>PRO STOCK APP</title>

<style>
body {{
    margin:0;
    font-family:Arial;
    background:#0b1220;
    color:white;
    text-align:center;
}}

.card {{
    background:#1e293b;
    padding:20px;
    margin:auto;
    margin-top:20px;
    width:900px;
    border-radius:12px;
    text-align:left;
}}

input {{
    padding:10px;
    border-radius:8px;
    border:none;
    width:200px;
}}

button {{
    padding:10px;
    border-radius:8px;
    border:none;
    cursor:pointer;
}}
</style>

</head>

<body>

<h1>🚀 PRO STOCK APP</h1>

<form method="POST">
    <input name="ticker" placeholder="NVDA, AAPL, TSLA">
    <button type="submit">Search</button>
</form>

{result}

</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
