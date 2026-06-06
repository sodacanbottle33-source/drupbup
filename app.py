from flask import Flask, request, session
import yfinance as yf
import plotly.graph_objects as go

app = Flask(__name__)
app.secret_key = "change_this_to_any_random_string"

# ---------------- AI STYLE EXPLANATION ----------------
def ai_explain(info):
    sector = info.get("sector", "Unknown")

    if sector == "Technology":
        return "Tech stock: high growth, high volatility, innovation-driven."
    elif sector == "Consumer Cyclical":
        return "Cyclical stock: depends on economy and consumer spending."
    elif sector == "Financial Services":
        return "Financial stock: affected by interest rates and banking cycles."
    elif sector == "Energy":
        return "Energy stock: tied to oil, gas, and global demand."
    else:
        return "Mixed sector: behavior depends on broader market conditions."

# ---------------- FORMAT MONEY ----------------
def fmt(num):
    try:
        if num is None:
            return "N/A"
        if num > 1_000_000_000_000:
            return f"${num/1_000_000_000_000:.2f}T"
        if num > 1_000_000_000:
            return f"${num/1_000_000_000:.2f}B"
        if num > 1_000_000:
            return f"${num/1_000_000:.2f}M"
        return f"${num:,.2f}"
    except:
        return "N/A"

# ---------------- MAIN APP ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    result = ""
    compare_chart = ""
    watchlist = session.get("watchlist", [])

    action = request.form.get("action") if request.method == "POST" else None

    # ---------------- SEARCH STOCK ----------------
    if action == "search":

        ticker = request.form["ticker"].upper()

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            price = stock.fast_info.get("lastPrice", 0)
            company = info.get("longName", ticker)

            hist_1m = stock.history(period="1mo")
            hist_6m = stock.history(period="6mo")

            # 1M chart
            fig1 = go.Figure()
            if not hist_1m.empty:
                fig1.add_trace(go.Scatter(x=hist_1m.index, y=hist_1m["Close"], name="1M"))
            fig1.update_layout(template="plotly_dark", height=300)
            chart1 = fig1.to_html(full_html=False)

            # 6M chart
            fig2 = go.Figure()
            if not hist_6m.empty:
                fig2.add_trace(go.Scatter(x=hist_6m.index, y=hist_6m["Close"], name="6M"))
            fig2.update_layout(template="plotly_dark", height=300)
            chart2 = fig2.to_html(full_html=False)

            ai = ai_explain(info)

            result = f"""
            <div class="card">
                <h2>{company}</h2>
                <h3>{ticker}</h3>

                <h2>Price: ${price}</h2>

                <p>{ai}</p>

                <hr>

                <p><b>Sector:</b> {info.get('sector','N/A')}</p>
                <p><b>Industry:</b> {info.get('industry','N/A')}</p>
                <p><b>Country:</b> {info.get('country','N/A')}</p>

                <hr>

                <p><b>Market Cap:</b> {fmt(info.get('marketCap'))}</p>

                <hr>

                <h3>1 Month Chart</h3>
                {chart1}

                <h3>6 Month Chart</h3>
                {chart2}

                <form method="POST">
                    <input type="hidden" name="ticker" value="{ticker}">
                    <button name="action" value="add_watchlist">Add to Watchlist</button>
                </form>
            </div>
            """

        except Exception as e:
            result = f"<div class='card'>Error: {e}</div>"

    # ---------------- WATCHLIST ----------------
    elif action == "add_watchlist":
        ticker = request.form["ticker"].upper()
        if ticker not in watchlist:
            watchlist.append(ticker)
        session["watchlist"] = watchlist

    # ---------------- COMPARE ----------------
    elif action == "compare":

        t1 = request.form["t1"].upper()
        t2 = request.form["t2"].upper()

        s1 = yf.Ticker(t1).history(period="3mo")
        s2 = yf.Ticker(t2).history(period="3mo")

        fig = go.Figure()

        if not s1.empty:
            fig.add_trace(go.Scatter(x=s1.index, y=s1["Close"], name=t1))

        if not s2.empty:
            fig.add_trace(go.Scatter(x=s2.index, y=s2["Close"], name=t2))

        fig.update_layout(template="plotly_dark", height=400)

        compare_chart = f"""
        <div class="card">
            <h3>Comparison</h3>
            {fig.to_html(full_html=False)}
        </div>
        """

    watch_html = "<br>".join(watchlist) if watchlist else "No stocks saved"

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
    width: 1000px;
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

.watchlist {{
    background: #111827;
    padding: 10px;
    margin-top: 20px;
}}
</style>

</head>

<body>

<div class="container">

<h1>Stock App Pro</h1>

<form method="POST">
    <input name="ticker" placeholder="NVDA, TSLA, AAPL">
    <button name="action" value="search">Search</button>
</form>

<form method="POST">
    <input name="t1" placeholder="Stock 1">
    <input name="t2" placeholder="Stock 2">
    <button name="action" value="compare">Compare</button>
</form>

<div class="watchlist">
<h3>Watchlist</h3>
{watch_html}
</div>

{result}

{compare_chart}

</div>

</body>
</html>
"""

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)