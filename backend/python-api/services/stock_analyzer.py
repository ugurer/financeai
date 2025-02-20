import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from typing import Dict, List, Tuple
import yfinance as yf
from datetime import datetime, timedelta
import ta
import joblib
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup

class StockAnalyzer:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.model = self._build_model()
        
    def _build_model(self) -> Sequential:
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

    def _prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        scaled_data = self.scaler.fit_transform(data['Close'].values.reshape(-1, 1))
        X, y = [], []
        
        for i in range(60, len(scaled_data)):
            X.append(scaled_data[i-60:i, 0])
            y.append(scaled_data[i, 0])
            
        return np.array(X), np.array(y)

    def _calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        # Trend İndikatörleri
        data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
        data['EMA_20'] = ta.trend.ema_indicator(data['Close'], window=20)
        data['MACD'] = ta.trend.macd_diff(data['Close'])
        
        # Momentum İndikatörleri
        data['RSI'] = ta.momentum.rsi(data['Close'])
        data['Stoch'] = ta.momentum.stoch(data['High'], data['Low'], data['Close'])
        
        # Volatilite İndikatörleri
        data['BB_upper'], data['BB_middle'], data['BB_lower'] = ta.volatility.bollinger_bands(data['Close'])
        data['ATR'] = ta.volatility.average_true_range(data['High'], data['Low'], data['Close'])
        
        # Hacim İndikatörleri
        data['OBV'] = ta.volume.on_balance_volume(data['Close'], data['Volume'])
        
        return data

    def _get_sentiment_analysis(self, symbol: str) -> float:
        try:
            # Haber başlıklarını topla
            url = f"https://finans.mynet.com/borsa/hisseler/{symbol.lower()}-detay/"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            news_titles = soup.find_all('h3', class_='news-title')
            
            # Duygu analizi yap
            sentiments = []
            for title in news_titles:
                analysis = TextBlob(title.text)
                sentiments.append(analysis.sentiment.polarity)
            
            return np.mean(sentiments) if sentiments else 0
            
        except Exception:
            return 0

    def analyze_stock(self, symbol: str) -> Dict:
        # Veri çek
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        stock = yf.Ticker(symbol + '.IS')
        data = stock.history(start=start_date, end=end_date)
        
        if data.empty:
            raise ValueError(f"No data found for symbol {symbol}")

        # Teknik analiz
        data = self._calculate_technical_indicators(data)
        
        # LSTM ile fiyat tahmini
        X, y = self._prepare_data(data)
        if len(X) > 0:
            self.model.fit(X, y, epochs=50, batch_size=32, verbose=0)
            last_60_days = self.scaler.transform(data['Close'].values[-60:].reshape(-1, 1))
            next_day_price = self.model.predict(last_60_days.reshape(1, 60, 1))
            next_day_price = self.scaler.inverse_transform(next_day_price)[0][0]
        else:
            next_day_price = data['Close'].iloc[-1]

        # Duygu analizi
        sentiment_score = self._get_sentiment_analysis(symbol)
        
        # Teknik göstergelerin son değerleri
        current_price = data['Close'].iloc[-1]
        rsi = data['RSI'].iloc[-1]
        macd = data['MACD'].iloc[-1]
        
        # Trend analizi
        short_term_trend = "YÜKSELIŞ" if data['EMA_20'].iloc[-1] > data['SMA_20'].iloc[-1] else "DÜŞÜŞ"
        long_term_trend = "YÜKSELIŞ" if data['Close'].iloc[-1] > data['SMA_20'].iloc[-1] else "DÜŞÜŞ"
        
        # Risk analizi
        volatility = data['Close'].pct_change().std() * np.sqrt(252)  # Yıllık volatilite
        risk_level = "YÜKSEK" if volatility > 0.3 else "ORTA" if volatility > 0.15 else "DÜŞÜK"
        
        # Destek ve direnç seviyeleri
        support = data['BB_lower'].iloc[-1]
        resistance = data['BB_upper'].iloc[-1]
        
        # Kısa vadeli analiz (1-7 gün)
        short_term_analysis = {
            "trend": short_term_trend,
            "next_day_forecast": next_day_price,
            "support_level": support,
            "resistance_level": resistance,
            "rsi_signal": "AŞIRI SATIŞ" if rsi < 30 else "AŞIRI ALIŞ" if rsi > 70 else "NÖTR",
            "confidence": 0.7
        }
        
        # Uzun vadeli analiz (1-6 ay)
        long_term_analysis = {
            "trend": long_term_trend,
            "forecast": current_price * (1 + (macd / current_price)),
            "risk_level": risk_level,
            "volatility": volatility,
            "sentiment": "POZİTİF" if sentiment_score > 0 else "NEGATİF" if sentiment_score < 0 else "NÖTR",
            "confidence": 0.6
        }
        
        # Öneriler
        recommendations = []
        
        # RSI bazlı öneri
        if rsi < 30:
            recommendations.append("RSI aşırı satış bölgesinde, alım fırsatı olabilir.")
        elif rsi > 70:
            recommendations.append("RSI aşırı alış bölgesinde, kar realizasyonu düşünülebilir.")
            
        # Trend bazlı öneri
        if short_term_trend == "YÜKSELIŞ" and long_term_trend == "YÜKSELIŞ":
            recommendations.append("Hem kısa hem uzun vadeli trend yukarı yönlü, pozisyon artırılabilir.")
        elif short_term_trend == "DÜŞÜŞ" and long_term_trend == "DÜŞÜŞ":
            recommendations.append("Hem kısa hem uzun vadeli trend aşağı yönlü, temkinli olunmalı.")
            
        # Bollinger Bandı bazlı öneri
        if data['Close'].iloc[-1] < data['BB_lower'].iloc[-1]:
            recommendations.append("Fiyat alt banda yakın, teknik olarak alım bölgesinde.")
        elif data['Close'].iloc[-1] > data['BB_upper'].iloc[-1]:
            recommendations.append("Fiyat üst banda yakın, teknik olarak satım bölgesinde.")
            
        return {
            "symbol": symbol,
            "current_price": current_price,
            "short_term_analysis": short_term_analysis,
            "long_term_analysis": long_term_analysis,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
