import joblib
import yfinance as yf
import tensorflow as tf
import pandas_ta as ta

def predict_tomorrow_live(model='final_gold_model.keras', scaler_x_path='gold_scaler_X.pkl', scaler_y_path='gold_scaler_Y.pkl'):
    # Load model
    model = tf.keras.models.load_model(model, compile=False)
    # 1. Load Scalers
    scaler_X = joblib.load(scaler_x_path)
    scaler_y = joblib.load(scaler_y_path)

    # 1. Fetch the last 60 days of data
    # (We fetch 60 to ensure we have enough rows to calculate 20-day SMAs/indicators)
    print("Fetching live market data...")
    live_data = yf.download("GC=F", period="60d", interval="1d")
    live_data.columns = live_data.columns.get_level_values(0)

    # 2. Apply the exact same Feature Engineering as training
    live_data["SMA_20"] = ta.sma(live_data['Close'], 20)

    # Calculating EMA feature
    live_data["EMA_20"] = ta.ema(live_data['Close'], 20)

    # Calculating the RSI
    live_data['RSI_14'] = ta.rsi(live_data['Close'], 14)

    # calculating the Bbands
    bb_cols = ("BBL_20", "BBM_20", "BBU_20", "BBB_20", "BBP_20")
    # unpack the result into  dataframe
    live_data[list(bb_cols)] = ta.bbands(live_data['Close'], length=20, std=2.0)

    live_data['ATR_14'] = ta.atr(live_data['High'], live_data['Low'], live_data['Close'], length=14)

    # 3. Drop rows with NaNs (the first 20 rows used for SMA calculation)
    df_final = live_data.dropna()

    # 2. Prepare the Input Window (Last 29 days)
    feature_cols = ['Close', 'SMA_20', 'EMA_20', 'RSI_14', 'BBL_20', 'BBU_20', 'ATR_14']
    last_window_raw = df_final[feature_cols].tail(29)

    # 3. Scale and Reshape Input
    last_window_scaled = scaler_X.transform(last_window_raw)
    last_window_3d = last_window_scaled.reshape(1, 29, len(feature_cols))

    # 4. Run Model Prediction
    pred_scaled = model.predict(last_window_3d)

    # 5. Inverse Transform the Result to USD
    pred_usd = scaler_y.inverse_transform(pred_scaled)[0][0]

    # 6. Directional Logic
    current_price = df_final['Close'].iloc[-1]
    change = pred_usd - current_price
    direction = "BULLISH (UP)" if change > 0 else "BEARISH (DOWN)"

    print("======================================")
    print(f"LATEST CLOSE PRICE: ${current_price:.2f}")
    print(f"PREDICTED PRICE FOR TOMORROW: ${pred_usd:.2f}")
    print(f"EXPECTED CHANGE: ${change:.2f} ({direction})")
    print("======================================")

    return pred_usd

# Usage (assuming df_final is your updated dataframe):
# price_tomorrow = predict_tomorrow_live(df_final, model)