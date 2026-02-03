# Gold Price Prediction API

A FastAPI-based REST API for predicting gold prices using an LSTM deep learning model.
Website Live at: https://goldpricepredictionfrontend.vercel.app/

## Features

- 🔮 Predict tomorrow's gold price based on live market data
- 📊 Technical indicators: SMA, EMA, RSI, Bollinger Bands, ATR
- 🚀 Fast and efficient predictions using TensorFlow
- 📡 RESTful API with automatic documentation
- 🌐 CORS enabled for web applications

## API Endpoints

### Health Check
```
GET /
GET /health
```

### Predict Gold Price
```
POST /api/predict
```

**Request Body (Optional):**
```json
{
  "model_path": "Model/final_gold_model.keras",
  "scaler_x_path": "Model/gold_scaler_X.pkl",
  "scaler_y_path": "Model/gold_scaler_Y.pkl"
}

```

**Response:**
```json
{
  "current_price": 2650.50,
  "predicted_price": 2665.30,
  "price_change": 14.80,
  "direction": "BULLISH (UP)",
  "status": "success"
}
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API:
```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

3. Access the API:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## Deployment to Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Select "Docker" as the SDK
3. Upload all files including:
   - `app.py`
   - `Inference.py`
   - `requirements.txt`
   - `Model/` directory with model files
4. The API will be automatically deployed

## Project Structure

```
Gold_Price_Prediction/
├── app.py                      # FastAPI application
├── Inference.py                # Prediction logic
├── requirements.txt            # Python dependencies
├── Model/
│   ├── final_gold_model.keras  # Trained LSTM model
│   ├── gold_scaler_X.pkl       # Feature scaler
│   └── gold_scaler_Y.pkl       # Target scaler
└── README.md                   # This file
```

## Model Details

- **Architecture**: LSTM (Long Short-Term Memory)
- **Input Features**: Close, SMA_20, EMA_20, RSI_14, BBL_20, BBU_20, ATR_14
- **Window Size**: 29 days
- **Data Source**: Yahoo Finance (GC=F - Gold Futures)

## Usage Example

### Python
```python
import requests

response = requests.post("http://localhost:8000/api/predict")
data = response.json()

print(f"Current Price: ${data['current_price']}")
print(f"Predicted Price: ${data['predicted_price']}")
print(f"Direction: {data['direction']}")
```

### cURL
```bash
curl -X POST http://localhost:8000/api/predict
```

### JavaScript
```javascript
fetch('http://localhost:8000/api/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

## License

MIT
