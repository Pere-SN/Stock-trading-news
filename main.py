import requests
import os
from twilio.rest import Client
from datetime import datetime as dt
from datetime import timedelta as td

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_URL = "https://www.alphavantage.co/query"
NEWS_URL = "https://newsapi.org/v2/everything"

# --------------------Twilio sid and token----------------
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)
# --------------------------------------------------------

# ---------------------------Stock Data-------------------
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": os.environ['STOCK_API']
}

stock_data = requests.get(STOCK_URL, params=stock_params).json()
# --------------------------------------------------------

# ---------------------------News Data--------------------
# Formated date from today and 5 days ago
today = dt.today().strftime(f"%Y-%m-%d")
five_days_ago = (dt.now() - td(days=5)).strftime("%Y-%m-%d")

news_params = {
    "qInTitle": COMPANY_NAME,
    "Date published": "yesterday",
    "Language": "en",
    "from": today,
    "to": five_days_ago,
    "apiKey": os.environ['NEWS_API']
}
news_data = requests.get(NEWS_URL, params=news_params).json()
# --------------------------------------------------------

# List with the value of the stock from yesterday and the day before yesterday.
stock_prc = [float(list(stock_data["Time Series (Daily)"].values())[0]["4. close"]),
             float(list(stock_data["Time Series (Daily)"].values())[1]["4. close"])]

# Calculates the difference in % between yesterday and before yesterday stock price.
value_diff = ((stock_prc[0] - stock_prc[1]) / stock_prc[0]) * 100

# Check if value is positive or negative
up_down = None
if value_diff > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

# Send SMS if the difference in stock value is bigger than 5% in the last 2 days and format the news
if abs(value_diff) > 5:
    for article in news_data["articles"][:3]:
        news = f"{STOCK}: {up_down}{round(value_diff)}\nHeadline: {article['title']}\nBrief: {article['description']}\n"
        message = client.messages.create(
            body=news,
            from_='twilio_number',
            to='your number'
        )
        print(message.status)

