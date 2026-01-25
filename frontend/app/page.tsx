'use client';

import { useState } from 'react';
import { predictGoldPrice } from '@/lib/api';

interface PredictionResult {
  current_price: number;
  predicted_price: number;
  price_change: number;
  direction: string;
  status: string;
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [retrying, setRetrying] = useState(false);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setRetrying(false);

    try {
      // Show retry message if it takes longer (likely retrying)
      const retryTimeout = setTimeout(() => {
        setRetrying(true);
      }, 5000);

      const data = await predictGoldPrice();
      clearTimeout(retryTimeout);
      setResult(data);
      setRetrying(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get prediction');
      setRetrying(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-yellow-50 via-amber-50 to-orange-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            <span className="bg-gradient-to-r from-yellow-600 to-amber-600 bg-clip-text text-transparent">
              Gold Price Prediction
            </span>
          </h1>
          <p className="text-xl text-gray-600">
            AI-powered predictions for tomorrow's gold price
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
          {/* Prediction Button */}
          <div className="text-center mb-8">
            <button
              onClick={handlePredict}
              disabled={loading}
              className="bg-gradient-to-r from-yellow-500 to-amber-600 hover:from-yellow-600 hover:to-amber-700 text-white font-bold py-4 px-8 rounded-xl text-lg shadow-lg transform transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {loading ? (
                <span className="flex flex-col items-center justify-center">
                  <span className="flex items-center">
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    {retrying ? 'Retrying...' : 'Predicting...'}
                  </span>
                  {retrying && (
                    <span className="text-sm mt-2 opacity-90">
                      This may take a moment (model loading...)
                    </span>
                  )}
                </span>
              ) : (
                '🔮 Predict Gold Price'
              )}
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 font-medium mb-2">Error: {error}</p>
              {error.includes('500') || error.includes('Server error') ? (
                <div className="text-sm text-red-700 mt-2">
                  <p className="font-semibold">Troubleshooting:</p>
                  <ul className="list-disc list-inside mt-1 space-y-1">
                    <li>The prediction service may be initializing (first request can take longer)</li>
                    <li>Please wait a moment and try again</li>
                    <li>If the issue persists, the Hugging Face Space may need to be restarted</li>
                  </ul>
                </div>
              ) : null}
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="space-y-6">
              {/* Current Price */}
              <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl p-6 border-2 border-blue-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">
                      Current Gold Price
                    </p>
                    <p className="text-3xl font-bold text-blue-900">
                      ${result.current_price.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </p>
                  </div>
                  <div className="text-4xl">💰</div>
                </div>
              </div>

              {/* Predicted Price */}
              <div className="bg-gradient-to-r from-yellow-50 to-amber-50 rounded-xl p-6 border-2 border-yellow-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">
                      Predicted Price (Tomorrow)
                    </p>
                    <p className="text-3xl font-bold text-yellow-900">
                      ${result.predicted_price.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </p>
                  </div>
                  <div className="text-4xl">🔮</div>
                </div>
              </div>

              {/* Price Change & Direction */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                  className={`rounded-xl p-6 border-2 ${
                    result.price_change >= 0
                      ? 'bg-green-50 border-green-200'
                      : 'bg-red-50 border-red-200'
                  }`}
                >
                  <p className="text-sm font-medium text-gray-600 mb-2">
                    Expected Change
                  </p>
                  <p
                    className={`text-2xl font-bold ${
                      result.price_change >= 0
                        ? 'text-green-700'
                        : 'text-red-700'
                    }`}
                  >
                    {result.price_change >= 0 ? '+' : ''}
                    ${result.price_change.toLocaleString('en-US', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </p>
                </div>

                <div
                  className={`rounded-xl p-6 border-2 ${
                    result.direction.includes('BULLISH')
                      ? 'bg-green-50 border-green-200'
                      : 'bg-red-50 border-red-200'
                  }`}
                >
                  <p className="text-sm font-medium text-gray-600 mb-2">
                    Market Direction
                  </p>
                  <p
                    className={`text-2xl font-bold ${
                      result.direction.includes('BULLISH')
                        ? 'text-green-700'
                        : 'text-red-700'
                    }`}
                  >
                    {result.direction.includes('BULLISH') ? '📈' : '📉'}{' '}
                    {result.direction}
                  </p>
                </div>
              </div>

              {/* Percentage Change */}
              <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                <p className="text-sm font-medium text-gray-600 mb-2">
                  Percentage Change
                </p>
                <p
                  className={`text-2xl font-bold ${
                    result.price_change >= 0 ? 'text-green-700' : 'text-red-700'
                  }`}
                >
                  {result.price_change >= 0 ? '+' : ''}
                  {(
                    (result.price_change / result.current_price) *
                    100
                  ).toFixed(2)}
                  %
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Info Section */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            About This Prediction
          </h2>
          <div className="space-y-3 text-gray-600">
            <p>
              This prediction is powered by an advanced LSTM (Long Short-Term
              Memory) neural network model trained on historical gold price data.
            </p>
            <p>
              The model analyzes technical indicators including SMA, EMA, RSI,
              Bollinger Bands, and ATR to forecast tomorrow's gold price.
            </p>
            <p className="text-sm text-gray-500 pt-2">
              <strong>Note:</strong> This is a prediction tool and should not be
              used as the sole basis for investment decisions. Always consult
              with financial advisors before making investment choices.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

