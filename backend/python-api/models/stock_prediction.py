import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from typing import List, Dict, Union

class StockPredictionModel:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.model = self._build_model()
        
    def _build_model(self) -> Sequential:
        """
        Build LSTM model for stock price prediction
        
        Returns:
            Keras Sequential model
        """
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=(60, 1)),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def prepare_data(self, prices: List[float], sequence_length: int = 60) -> tuple:
        """
        Prepare data for LSTM model
        
        Args:
            prices: List of historical prices
            sequence_length: Length of input sequences
            
        Returns:
            Tuple of prepared X and y data
        """
        scaled_data = self.scaler.fit_transform(np.array(prices).reshape(-1, 1))
        X, y = [], []
        
        for i in range(sequence_length, len(scaled_data)):
            X.append(scaled_data[i-sequence_length:i, 0])
            y.append(scaled_data[i, 0])
            
        X = np.array(X)
        y = np.array(y)
        
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        return X, y
    
    def train(self, prices: List[float], epochs: int = 50, batch_size: int = 32):
        """
        Train the model on historical price data
        
        Args:
            prices: List of historical prices
            epochs: Number of training epochs
            batch_size: Training batch size
        """
        X, y = self.prepare_data(prices)
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
    
    def predict(self, prices: List[float], days_ahead: int = 30) -> Dict[str, List[float]]:
        """
        Make price predictions
        
        Args:
            prices: List of historical prices
            days_ahead: Number of days to predict ahead
            
        Returns:
            Dictionary containing predicted prices
        """
        last_sequence = np.array(prices[-60:])
        scaled_sequence = self.scaler.transform(last_sequence.reshape(-1, 1))
        
        predictions = []
        current_sequence = scaled_sequence.copy()
        
        for _ in range(days_ahead):
            # Prepare current sequence for prediction
            X = current_sequence[-60:].reshape(1, 60, 1)
            
            # Make prediction
            predicted_value = self.model.predict(X, verbose=0)[0, 0]
            predictions.append(predicted_value)
            
            # Update sequence for next prediction
            current_sequence = np.append(current_sequence, predicted_value)
            
        # Inverse transform predictions
        predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
        
        return {
            "predictions": predictions.flatten().tolist()
        }
    
    def evaluate_prediction(self, actual: List[float], predicted: List[float]) -> Dict[str, float]:
        """
        Evaluate prediction accuracy
        
        Args:
            actual: Actual prices
            predicted: Predicted prices
            
        Returns:
            Dictionary containing evaluation metrics
        """
        mse = np.mean((np.array(actual) - np.array(predicted)) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(np.array(actual) - np.array(predicted)))
        
        return {
            "mse": float(mse),
            "rmse": float(rmse),
            "mae": float(mae)
        }
