import requests
import pandas as pd

# Telegram Bot Details
TELEGRAM_BOT_TOKEN = "7669591712:AAE-IKrX5F6tdg1KAWTrtZl1vfOs3LAF3gI"  # Replace with your bot token
TELEGRAM_CHAT_ID = "5682982418"  # Replace with your chat ID

# Function to send a message to Telegram
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Message sent to Telegram!")
    else:
        print(f"Failed to send message: {response.text}")

# Fetch option chain data from NSE
def fetch_banknifty_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        records = data["records"]
        spot_price = records["underlyingValue"]  # Spot price of Bank Nifty
        options = []
        for record in records["data"]:
            for option_type in ["CE", "PE"]:
                if option_type in record:
                    options.append({
                        "Strike Price": record["strikePrice"],
                        "Type": option_type,
                        "Last Price": record[option_type]["lastPrice"],
                        "Open Interest": record[option_type]["openInterest"],
                        "Volume": record[option_type]["totalTradedVolume"],
                    })
        return pd.DataFrame(options), spot_price
    else:
        raise Exception("Failed to fetch data from NSE. Try again later.")

# Function to get Bank Nifty trend (Dummy logic - Replace with your actual logic)
def get_banknifty_trend():
    # Example: Fetching latest Bank Nifty trend from external API or using your own logic
    # For now, let's assume a simple rule:
    import random
    return random.choice(["BULLISH", "BEARISH", "NEUTRAL"])

# Generate signals for dynamic strike prices
def generate_signals(data, spot_price):
    trend = get_banknifty_trend()  # Get trend

    if trend == "NEUTRAL":
        print("Market is neutral. No signals generated.")
        return []

    nearest_strike = round(spot_price / 100) * 100
    selected_strikes = [
        nearest_strike - 200,
        nearest_strike - 100,
        nearest_strike,
        nearest_strike + 100,
        nearest_strike + 200,
    ]

    messages = []
    option_type = "CE" if trend == "BULLISH" else "PE"  # Choose based on trend
    
    for strike in selected_strikes:
        selected_option = data[
            (data["Strike Price"] == strike) & (data["Type"] == option_type)
        ]
        
        if selected_option.empty:
            continue

        # Extract single values safely
        last_price = selected_option["Last Price"].iloc[0] if not selected_option["Last Price"].isnull().all() else 0
        open_interest = selected_option["Open Interest"].iloc[0] if not selected_option["Open Interest"].isnull().all() else 0
        volume = selected_option["Volume"].iloc[0] if not selected_option["Volume"].isnull().all() else 0

        # Signal logic
        if volume > 100000 and open_interest > 10000 and last_price > 100:
            signal = "BUY"
            stop_loss = round(last_price * 0.90, 2)  # 10% below last price
            target_price = round(last_price * 1.15, 2)  # 15% above last price
        else:
            continue  # Ignore weak trades

        # Format the message
        message = (
            f"🔔 <b>Bank Nifty Option Signal Alert</b> 🔔\n\n"
            f"        📊 <b>Strike Price:</b> {strike}\n"
            f"        🔵 <b>Option Type:</b> {option_type}\n"
            f"        💰 <b>Last Price:</b> ₹{last_price}\n"
            f"        📉 <b>Open Interest:</b> {open_interest}\n"
            f"        🔄 <b>Volume:</b> {volume}\n"
            f"        📍 <b>Signal:</b> <b>{signal}</b>\n\n"
            f"        🎯 <b>Stop Loss:</b> ₹{stop_loss}\n"
            f"        🎯 <b>Target Price:</b> ₹{target_price}\n\n"
            f"        📢 <b>Advice:</b> Follow the signal with proper risk management."
        )
        messages.append(message)
    
    return messages

# Main function
if __name__ == "__main__":
    symbol = "BANKNIFTY"
    
    try:
        # Fetch option chain data and spot price
        option_data, spot_price = fetch_banknifty_option_chain(symbol)
        
        print(f"Spot Price: {spot_price}")
        print("Available Option Chain Data:")
        print(option_data)
        
        # Generate signals
        signals = generate_signals(option_data, spot_price)
        
        # Send signals to Telegram
        for signal in signals:
            send_to_telegram(signal)
    except Exception as e:
        print(f"An error occurred: {e}")