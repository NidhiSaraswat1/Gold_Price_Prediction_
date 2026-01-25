from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Import the prediction function from Inference.py
from Inference import predict_tomorrow_live

# Initialize FastAPI app
app = FastAPI(
    title="Gold Price Prediction API",
    description="API for predicting gold prices using LSTM model",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For Hugging Face Spaces - allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model (optional, for future extensions)
class PredictionRequest(BaseModel):
    model_path: Optional[str] = "Model/final_gold_model.keras"
    scaler_x_path: Optional[str] = "Model/gold_scaler_X.pkl"
    scaler_y_path: Optional[str] = "Model/gold_scaler_Y.pkl"

# Response model
class PredictionResponse(BaseModel):
    current_price: float
    predicted_price: float
    price_change: float
    direction: str
    status: str

@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "message": "Gold Price Prediction API is running",
        "status": "healthy",
        "endpoints": {
            "predict": "/api/predict",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {"status": "healthy"}

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_gold_price(request: PredictionRequest = None):
    """
    Predict tomorrow's gold price
    
    Parameters:
    - model_path: Path to the trained model (default: Model/final_gold_model.keras)
    - scaler_x_path: Path to X scaler (default: Model/gold_scaler_X.pkl)
    - scaler_y_path: Path to Y scaler (default: Model/gold_scaler_Y.pkl)
    
    Returns:
    - current_price: Current gold price
    - predicted_price: Predicted price for tomorrow
    - price_change: Expected change in price
    - direction: BULLISH (UP) or BEARISH (DOWN)
    """
    try:
        # Use default paths if request is None
        if request is None:
            request = PredictionRequest()
        
        # Call the prediction function from Inference.py
        # Note: We need to modify the function to return values instead of just printing
        # For now, we'll capture the prediction
        import io
        from contextlib import redirect_stdout
        
        # Import required libraries for the prediction
        import joblib
        import yfinance as yf
        import tensorflow as tf
        import pandas_ta_classic as ta
        import pandas as pd
        
        # Load model and scalers
        model = tf.keras.models.load_model(request.model_path, compile=False)
        scaler_X = joblib.load(request.scaler_x_path)
        scaler_y = joblib.load(request.scaler_y_path)

        # Fetch live data with retry logic and fallback methods
        # Note: Let yfinance handle the session internally (it uses curl_cffi)
        import time
        max_retries = 3
        live_data = None
        
        for attempt in range(max_retries):
            try:
                # Method 1: Try using yf.download (let YF handle session)
                try:
                    periods_to_try = ["90d", "60d", "30d"]
                    for period in periods_to_try:
                        try:
                            live_data = yf.download(
                                "GC=F", 
                                period=period, 
                                interval="1d", 
                                progress=False
                            )
                            # Handle MultiIndex columns
                            if isinstance(live_data.columns, pd.MultiIndex):
                                live_data.columns = live_data.columns.get_level_values(0)
                            
                            if not live_data.empty and len(live_data) > 0:
                                break
                        except Exception as period_error:
                            if period == periods_to_try[-1]:  # Last period attempt
                                raise period_error
                            continue
                    
                    if live_data is not None and not live_data.empty:
                        break
                        
                except Exception as download_error:
                    # Method 2: Fallback to using Ticker object (sometimes more reliable)
                    try:
                        ticker = yf.Ticker("GC=F")
                        live_data = ticker.history(period="90d", interval="1d")
                        if live_data.empty:
                            live_data = ticker.history(period="60d", interval="1d")
                        if live_data.empty:
                            live_data = ticker.history(period="30d", interval="1d")
                        
                        if not live_data.empty:
                            break
                    except Exception as ticker_error:
                        # If both methods fail, raise the original download error
                        raise download_error
                    
            except Exception as e:
                error_msg = str(e)
                error_type = type(e).__name__
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                    time.sleep(wait_time)
                    continue
                else:
                    if "JSONDecodeError" in error_type or "Expecting value" in error_msg:
                        raise ValueError(
                            "Failed to download market data: Yahoo Finance API returned invalid response (JSONDecodeError). "
                            "This may be due to rate limiting, API changes, or network issues. "
                            "Please try again in a few moments. If the issue persists, Yahoo Finance may be temporarily unavailable."
                        )
                    else:
                        raise ValueError(f"Failed to download market data after {max_retries} attempts: {error_msg}")
        
        if live_data is None or live_data.empty:
            raise ValueError("Failed to download market data: Received empty dataset from Yahoo Finance after all retry attempts.")
        
        # Validate data download
        if live_data.empty:
            raise ValueError("Failed to download market data. The data source may be unavailable or the market may be closed.")
        
        live_data.columns = live_data.columns.get_level_values(0)
        
        # Validate required columns exist
        required_cols = ['Close', 'High', 'Low']
        missing_cols = [col for col in required_cols if col not in live_data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in market data: {missing_cols}")
        
        # Feature engineering
        live_data["SMA_20"] = ta.sma(live_data['Close'], 20)
        live_data["EMA_20"] = ta.ema(live_data['Close'], 20)
        live_data['RSI_14'] = ta.rsi(live_data['Close'], 14)
        
        bb_cols = ("BBL_20", "BBM_20", "BBU_20", "BBB_20", "BBP_20")
        live_data[list(bb_cols)] = ta.bbands(live_data['Close'], length=20, std=2.0)
        live_data['ATR_14'] = ta.atr(live_data['High'], live_data['Low'], live_data['Close'], length=14)
        
        # Drop NaNs
        df_final = live_data.dropna()
        
        # Validate we have enough data after dropping NaNs
        if df_final.empty:
            raise ValueError("No valid data available after processing. Market data may be incomplete.")
        
        if len(df_final) < 29:
            raise ValueError(f"Insufficient data: Need at least 29 rows, but only have {len(df_final)} rows after processing.")
        
        # Prepare input
        feature_cols = ['Close', 'SMA_20', 'EMA_20', 'RSI_14', 'BBL_20', 'BBU_20', 'ATR_14']
        
        # Validate all feature columns exist
        missing_features = [col for col in feature_cols if col not in df_final.columns]
        if missing_features:
            raise ValueError(f"Missing feature columns: {missing_features}")
        
        last_window_raw = df_final[feature_cols].tail(29)
        
        # Validate the window has correct shape
        if last_window_raw.empty or len(last_window_raw) < 29:
            raise ValueError(f"Insufficient data for prediction window: Need 29 rows, got {len(last_window_raw)}")
        
        if last_window_raw.shape[1] != len(feature_cols):
            raise ValueError(f"Feature dimension mismatch: Expected {len(feature_cols)} features, got {last_window_raw.shape[1]}")
        
        # Check for any NaN values in the window
        if last_window_raw.isna().any().any():
            raise ValueError("NaN values found in prediction window. Data preprocessing may be incomplete.")
        
        # Ensure all values are numeric and finite
        if not last_window_raw.select_dtypes(include=['number']).shape[1] == len(feature_cols):
            raise ValueError("Non-numeric values found in feature columns.")
        
        # Check for infinite values
        numeric_data = last_window_raw.select_dtypes(include=['number'])
        if (numeric_data == float('inf')).any().any() or (numeric_data == float('-inf')).any().any():
            raise ValueError("Infinite values found in data. Please check data quality.")
        
        # Convert to numpy array and validate shape before scaling
        last_window_array = last_window_raw.values
        if last_window_array.shape != (29, len(feature_cols)):
            raise ValueError(f"Data shape mismatch: Expected (29, {len(feature_cols)}), got {last_window_array.shape}")
        
        # Scale and reshape
        last_window_scaled = scaler_X.transform(last_window_raw)
        last_window_3d = last_window_scaled.reshape(1, 29, len(feature_cols))
        
        # Predict
        pred_scaled = model.predict(last_window_3d, verbose=0)
        pred_usd = scaler_y.inverse_transform(pred_scaled)[0][0]
        
        # Calculate metrics
        current_price = float(df_final['Close'].iloc[-1])
        change = pred_usd - current_price
        direction = "BULLISH (UP)" if change > 0 else "BEARISH (DOWN)"
        
        return PredictionResponse(
            current_price=round(current_price, 2),
            predicted_price=round(float(pred_usd), 2),
            price_change=round(change, 2),
            direction=direction,
            status="success"
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Model or scaler file not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
