import yfinance as yf
import pandas as pd
import plotly.express as px

# Fidelity index funds
tickers = ["FNILX", "FZIPX", "FZROX", "FZILX"]

df = yf.download(tickers, period="1mo", interval="1d", group_by="ticker", auto_adjust=True)

data = list()

# loop, create copy, set index, extract ticker, sub DataFrame, append
for ticker in tickers:
    temp = df[ticker].copy()
    temp["Date"] = temp.index
    temp["Ticker"] = ticker
    temp["PctChange"] = temp["Close"].pct_change() * 100
    temp["PctChange"] = temp["PctChange"].cumsum()
    temp = temp[["Date", "PctChange", "Ticker"]]
    data.append(temp)

 # combine dataframes
final_df = pd.concat(data)

fig = px.line(final_df, x="Date", y="PctChange", color="Ticker",
              title="Fidelity Index Funds",
              labels={"PctChange": "Cumulative Percent Change"})
fig.show()