const API_URL = 'https://nidhisarai-gold-price-prediction.hf.space';

export interface PredictionResponse {
  current_price: number;
  predicted_price: number;
  price_change: number;
  direction: string;
  status: string;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

export async function predictGoldPrice(retries: number = 2): Promise<PredictionResponse> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      // Create an AbortController for timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 90000); // 90 second timeout (model loading can take time)

      try {
        const response = await fetch(`${API_URL}/api/predict`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          // Send empty body as the API accepts optional request
          body: JSON.stringify({}),
          signal: controller.signal,
          mode: 'cors',
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          // Try to get error details from the response
          let errorMessage = `API request failed: ${response.status} ${response.statusText}`;
          try {
            const errorData = await response.json();
            if (errorData.detail) {
              errorMessage = errorData.detail;
            } else if (errorData.message) {
              errorMessage = errorData.message;
            }
          } catch (e) {
            // If we can't parse the error response, use the status text
            try {
              const errorText = await response.text();
              if (errorText) {
                errorMessage = errorText;
              }
            } catch (textError) {
              // If we can't get text either, use the status
              if (response.status === 500) {
                errorMessage = `Server error (500): The prediction service encountered an error. This may happen if the model is still loading. Please try again in a few moments.`;
              } else {
                errorMessage = `Server error (${response.status}). The prediction service may be experiencing issues.`;
              }
            }
          }
          
          // For 500 errors, retry if we have attempts left
          if (response.status === 500 && attempt < retries) {
            lastError = new Error(errorMessage);
            // Wait before retrying (exponential backoff)
            await new Promise(resolve => setTimeout(resolve, 2000 * (attempt + 1)));
            continue;
          }
          
          throw new Error(errorMessage);
        }

        const data = await response.json();
        return data;
      } catch (fetchError) {
        clearTimeout(timeoutId);
        
        if (fetchError instanceof Error) {
          if (fetchError.name === 'AbortError') {
            lastError = new Error('Request timeout: The prediction is taking too long. Please try again.');
            if (attempt < retries) {
              await new Promise(resolve => setTimeout(resolve, 2000 * (attempt + 1)));
              continue;
            }
            throw lastError;
          }
          
          // Retry on network errors
          if ((fetchError.message.includes('fetch') || fetchError.message.includes('Failed to fetch')) && attempt < retries) {
            lastError = fetchError;
            await new Promise(resolve => setTimeout(resolve, 2000 * (attempt + 1)));
            continue;
          }
          
          throw fetchError;
        }
        throw fetchError;
      }
    } catch (error) {
      if (error instanceof Error) {
        // Check if it's a network error
        if (error.message.includes('fetch') || error.message.includes('Failed to fetch')) {
          lastError = new Error('Network error: Unable to connect to the API. Please check your internet connection and try again.');
          if (attempt < retries) {
            await new Promise(resolve => setTimeout(resolve, 2000 * (attempt + 1)));
            continue;
          }
          throw lastError;
        }
        throw error;
      }
      throw new Error('Failed to fetch prediction: Unknown error');
    }
  }

  // If we've exhausted all retries
  throw lastError || new Error('Failed to fetch prediction after multiple attempts');
}

