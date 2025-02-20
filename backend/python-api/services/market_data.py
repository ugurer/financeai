import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class MarketDataService:
    @staticmethod
    def get_stock_data(symbol: str, period: str = "1mo") -> Dict:
        """
        Hisse senedi verilerini Yahoo Finance'den alır
        """
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            
            if hist.empty:
                raise ValueError(f"Veri bulunamadı: {symbol}")
            
            latest_price = hist['Close'][-1]
            previous_close = hist['Close'][-2] if len(hist) > 1 else latest_price
            daily_change = latest_price - previous_close
            daily_change_percentage = (daily_change / previous_close) * 100
            
            return {
                "symbol": symbol,
                "current_price": latest_price,
                "daily_change": daily_change,
                "daily_change_percentage": daily_change_percentage,
                "history": hist['Close'].to_dict(),
                "volume": hist['Volume'][-1],
                "info": {
                    "name": stock.info.get('longName', symbol),
                    "sector": stock.info.get('sector', 'Unknown'),
                    "industry": stock.info.get('industry', 'Unknown'),
                    "market_cap": stock.info.get('marketCap', None),
                    "pe_ratio": stock.info.get('trailingPE', None),
                    "dividend_yield": stock.info.get('dividendYield', None)
                }
            }
        except Exception as e:
            raise Exception(f"Hisse senedi verisi alınırken hata oluştu ({symbol}): {str(e)}")
    
    @staticmethod
    def get_market_summary() -> Dict:
        """
        Piyasa özet verilerini getirir
        """
        try:
            # Örnek endeksler
            indices = ['^BIST100', '^XU030', '^XUSIN']
            summary = {}
            
            for index in indices:
                data = yf.Ticker(index)
                hist = data.history(period="1d")
                
                if not hist.empty:
                    latest = hist.iloc[-1]
                    summary[index] = {
                        "name": data.info.get('longName', index),
                        "last_price": latest['Close'],
                        "change": latest['Close'] - latest['Open'],
                        "change_percent": ((latest['Close'] - latest['Open']) / latest['Open']) * 100
                    }
            
            return summary
        except Exception as e:
            raise Exception(f"Piyasa özeti alınırken hata oluştu: {str(e)}")
    
    @staticmethod
    def get_stock_recommendations(symbols: List[str]) -> List[Dict]:
        """
        Hisse senetleri için öneriler oluşturur
        """
        recommendations = []
        
        try:
            for symbol in symbols:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="6mo")
                
                if not hist.empty:
                    # Basit teknik analiz
                    current_price = hist['Close'][-1]
                    ma50 = hist['Close'].rolling(window=50).mean()[-1]
                    ma200 = hist['Close'].rolling(window=200).mean()[-1]
                    
                    rsi = MarketDataService._calculate_rsi(hist['Close'])
                    
                    recommendation = {
                        "symbol": symbol,
                        "name": stock.info.get('longName', symbol),
                        "current_price": current_price,
                        "signals": {
                            "ma50_signal": "buy" if current_price > ma50 else "sell",
                            "ma200_signal": "buy" if current_price > ma200 else "sell",
                            "rsi_signal": "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"
                        },
                        "metrics": {
                            "pe_ratio": stock.info.get('trailingPE', None),
                            "price_to_book": stock.info.get('priceToBook', None),
                            "dividend_yield": stock.info.get('dividendYield', None)
                        }
                    }
                    
                    recommendations.append(recommendation)
            
            return recommendations
        except Exception as e:
            raise Exception(f"Öneriler oluşturulurken hata oluştu: {str(e)}")
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, periods: int = 14) -> float:
        """
        Göreceli Güç Endeksi (RSI) hesaplar
        """
        delta = prices.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] 