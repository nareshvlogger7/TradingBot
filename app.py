from flask import Flask, request, jsonify, render_template
from smartapi.smartConnect import SmartConnect
import pandas as pd
import requests

app = Flask(__name__)

# Initialize Symbol to Token Map
def initialize_symbol_to_token_map():
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    token_df = pd.DataFrame.from_dict(requests.get(url).json())
    token_df['expiry'] = pd.to_datetime(token_df['expiry'])
    token_df = token_df.astype({'strike': 'float'})
    return token_df

# Fetch Token Information
def get_token_info(token_map, exch_seg, instrumenttype, symbol, strike_price, pe_ce):
    strike_price = strike_price * 100
    if exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        df = token_map[(token_map['exch_seg'] == exch_seg) & 
                       (token_map['instrumenttype'] == instrumenttype) & 
                       (token_map['name'] == symbol) & 
                       (token_map['strike'] == strike_price)]
        return df[df['exch_seg'] == 'NFO'][(df['instrumenttype'] == instrumenttype)]

# Place an Order
def place_order(obj, token, symbol, qty, exch_seg, buy_sell, ordertype, price):
    try:
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": buy_sell,
            "exchange": exch_seg,
            "ordertype": ordertype,
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": price,
            "squareoff": "0",
            "stoploss": "0",
            "quantity": qty
        }
        orderobj = obj.placeOrder(orderparams)
        return {"status": "success", "order_id": orderobj['orderId']}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Fetch account balance
def get_account_balance(obj):
    try:
        # This is an example endpoint; you will need to use the actual API method to get the account balance.
        account_data = obj.getAccountDetails()
        return float(account_data['data']['balance'])
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_trading', methods=['POST'])
def start_trading():
    data = request.json
    api_key = data['apiKey']
    username = data['username']
    token = data['token']
    stop_loss_percent = float(data['stopLoss'])
    profit_target_percent = float(data['profit'])
    
    # Create a session with the provided credentials
    obj = SmartConnect(api_key=api_key)
    data = obj.generateSession(username, token)
    refresh_token = data['data']['refreshToken']
    
    # Initialize Symbol to Token Map
    token_map = initialize_symbol_to_token_map()

    # Example of trading logic using NIFTY options
    symbol = "NIFTY"
    strike_price = 15800  # Example strike price
    token_info = get_token_info(token_map, 'NFO', 'OPTIDX', symbol, strike_price, 'CE').iloc[0]
    
    token = token_info['token']
    ltp = obj.ltpData('NFO', token_info['name'], token)['data']['ltp']

    # Calculate Stop Loss and Profit Target Prices
    stop_loss_price = ltp * (1 - stop_loss_percent / 100)
    profit_target_price = ltp * (1 + profit_target_percent / 100)

    # Fetch available account balance
    available_balance = get_account_balance(obj)
    
    # Calculate quantity based on balance and LTP
    qty = int(available_balance // ltp)  # Calculate number of lots that can be purchased
    if qty < 1:
        return jsonify({"status": "error", "message": "Insufficient balance to place an order."})
    
    # Place a buy order
    order_response = place_order(obj, token, token_info['name'], qty, 'NFO', 'BUY', 'LIMIT', ltp)
    
    return jsonify(order_response)

if __name__ == '__main__':
    app.run(debug=True)
