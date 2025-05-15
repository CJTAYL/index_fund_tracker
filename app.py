import plotly.io as pio
import plotly.express as px
import pandas as pd
import yfinance as yf
from flask import Flask, render_template, request

app = Flask(__name__)

TICKER_OPTIONS = ["FNILX", "FZIPX", "FZROX", "FZILX"]

@app.route("/", methods=["GET"])
def landing():
    return render_template("index.html", tickers=TICKER_OPTIONS)

@app.route("/chart", methods=["POST"])
def chart():
    selected_tickers = request.form.getlist("tickers")
    selected_period = request.form.get("period", "1mo") # default period

    if not selected_tickers:
        return "<h3>No tickers selected. Please go back and choose at least one."

    df = yf.download(selected_tickers, period=selected_period, interval="1d", group_by="ticker", auto_adjust=True)

    data = list()

    # loop, create copy, set index, extract ticker, sub DataFrame, append
    for ticker in selected_tickers:
        temp = df[ticker].copy()
        temp["Date"] = temp.index
        temp["Ticker"] = ticker
        temp["PctChange"] = temp["Close"].pct_change() * 100
        temp["PctChange"] = temp["PctChange"].cumsum()
        temp["Normalized"] = temp["Close"] / temp["Close"].iloc[0]
        temp = temp[["Date", "PctChange", "Normalized", "Ticker"]]
        data.append(temp)

    # combine dataframes
    final_df = pd.concat(data)

    # get most reent closing prices
    latest_prices = {
        ticker: round(df[ticker]["Close"].dropna().iloc[-1], 2)
        for ticker in selected_tickers
    }

    fig_pct = px.line(final_df, x="Date", y="PctChange", color="Ticker",
                  title="Cumulative Percent Change",
                  labels={"PctChange": "Cumulative Percent Change"})

    fig_norm = px.line(final_df, x="Date", y="Normalized", color="Ticker",
                       title="Normalized Price (Relative to Start)",
                       labels={"Normalized": "Price (Start = 1.0)"})

    plot_html_pct = pio.to_html(fig_pct, full_html=False)
    plot_html_norm = pio.to_html(fig_norm, full_html=False)

    return render_template("chart.html",
                           plot_pct=plot_html_pct,
                           plot_norm=plot_html_norm,
                           latest_prices=latest_prices)

if __name__ == '__main__':
    app.run(debug=True)