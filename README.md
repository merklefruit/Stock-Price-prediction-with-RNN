### (Find More about this project on [my website](https://nicolasracchi.com/blog/stock_price_prediction))

# Stock-Price-prediction-with-RNN

This web app is build with Flask in python.

## Example of prediction output:

![The output graph from the web app](nvda_prediction.png)

## Instructions to run:

1. CD in the trading_bot directory

2. If you're on MacOS/Linux:  `export FLASK_APP=app.py`
    
    If you're on Windows: `set FLASK_APP=app.py`

3. (Optional): Set up your python virtual environment

3. Install requirements: `pip install -r requirements.txt`

4. Start the app: `flask run`

## How it works:

* Stock historical data is gathered from the Alpha Vantage API
* An LSTM RNN is trained with your choice of stock symbol, with the API data
* The network is used to predict prices from 1/1/2019 on forward.
* When the prediction has been completed, you'll see a graph of the ACTUAL vs PREDICTED stock price.


## Disclaimer:

This project was made in 1 day and it was meant to learn about RNNs and web development.

This is not meant to be an investment guide.
