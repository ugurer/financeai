from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PYTHON_API_PORT = int(os.getenv('PYTHON_API_PORT', '8000'))
JWT_SECRET = os.getenv('JWT_SECRET', 'your_jwt_secret_here')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')

app = FastAPI(title="Finance AI API")

# CORS ayarları
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioOptimizationRequest(BaseModel):
    symbols: List[str]
    risk_profile: str
    constraints: Optional[Dict] = None

class StockData(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    volume: int

class MarketSummary(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    volume: int

class Recommendation(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    recommendation: str
    confidence: float
    reason: str

class PortfolioStock(BaseModel):
    symbol: str
    name: str
    quantity: int
    averagePrice: float
    currentPrice: float
    totalValue: float
    profit: float
    profitPercentage: float

class Portfolio(BaseModel):
    id: int
    userId: int
    stocks: List[PortfolioStock]
    totalValue: float
    dailyChange: float
    lastUpdated: str

class AddToPortfolioRequest(BaseModel):
    symbol: str
    quantity: int
    price: float

# Türk hisse senetleri listesi ve mock verileri
TURKISH_STOCKS: Dict[str, Dict[str, any]] = {
    'THYAO.IS': {
        'name': 'Türk Hava Yolları',
        'price': 150.20,
        'change': 2.5,
        'volume': 15000000
    },
    'GARAN.IS': {
        'name': 'Garanti Bankası',
        'price': 85.30,
        'change': -1.2,
        'volume': 12000000
    },
    'AKBNK.IS': {
        'name': 'Akbank',
        'price': 92.45,
        'change': 1.8,
        'volume': 10000000
    },
    'EREGL.IS': {
        'name': 'Ereğli Demir Çelik',
        'price': 45.60,
        'change': 0.5,
        'volume': 8000000
    },
    'ASELS.IS': {
        'name': 'Aselsan',
        'price': 78.90,
        'change': 3.2,
        'volume': 6000000
    },
    'KCHOL.IS': {
        'name': 'Koç Holding',
        'price': 120.50,
        'change': 1.5,
        'volume': 9000000
    },
    'SISE.IS': {
        'name': 'Şişe Cam',
        'price': 35.80,
        'change': -0.8,
        'volume': 5000000
    },
    'TUPRS.IS': {
        'name': 'Tüpraş',
        'price': 180.30,
        'change': 2.8,
        'volume': 7000000
    },
    'TAVHL.IS': {
        'name': 'TAV Havalimanları',
        'price': 65.40,
        'change': -1.5,
        'volume': 4000000
    },
    'PGSUS.IS': {
        'name': 'Pegasus',
        'price': 95.70,
        'change': 1.7,
        'volume': 3500000
    }
}

# Mock portföy verisi
MOCK_PORTFOLIO = {
    1: {
        "id": 1,
        "userId": 1,
        "stocks": [
            {
                "symbol": "THYAO",
                "name": "Türk Hava Yolları",
                "quantity": 100,
                "averagePrice": 145.30,
                "currentPrice": 150.20,
                "totalValue": 15020.00,
                "profit": 490.00,
                "profitPercentage": 3.37
            },
            {
                "symbol": "GARAN",
                "name": "Garanti Bankası",
                "quantity": 200,
                "averagePrice": 82.50,
                "currentPrice": 85.30,
                "totalValue": 17060.00,
                "profit": 560.00,
                "profitPercentage": 3.39
            }
        ],
        "totalValue": 32080.00,
        "dailyChange": 3.38,
        "lastUpdated": "2025-02-20T14:30:00Z"
    }
}

# Servis örnekleri
market_service = None
portfolio_optimizer = None
risk_analyzer = None
stock_analyzer = None

@app.get("/api/market/summary", response_model=List[MarketSummary])
async def get_market_summary():
    """
    Piyasa özetini döndürür. Mock veri kullanır.
    """
    try:
        summaries = []
        for symbol, data in TURKISH_STOCKS.items():
            summaries.append(MarketSummary(
                symbol=symbol.replace('.IS', ''),  # .IS uzantısını kaldır
                name=data['name'],
                price=data['price'],
                change=data['change'],
                volume=data['volume']
            ))
        return summaries
    except Exception as e:
        logger.error(f"Piyasa özeti alınırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Piyasa verileri alınamadı")

@app.get("/api/market/recommendations", response_model=List[Recommendation])
async def get_recommendations():
    """
    Hisse senedi önerilerini döndürür. Mock veri kullanır.
    """
    try:
        recommendations = []
        for symbol, data in TURKISH_STOCKS.items():
            # Basit öneri algoritması
            if data['change'] > 2:
                rec = "sat"
                reason = "Aşırı alım bölgesinde"
                confidence = 0.8
            elif data['change'] < -2:
                rec = "al"
                reason = "Aşırı satım bölgesinde"
                confidence = 0.8
            else:
                rec = "tut"
                reason = "Nötr bölgede"
                confidence = 0.6

            recommendations.append(Recommendation(
                symbol=symbol.replace('.IS', ''),  # .IS uzantısını kaldır
                name=data['name'],
                price=data['price'],
                change=data['change'],
                recommendation=rec,
                confidence=confidence,
                reason=reason
            ))
        return recommendations
    except Exception as e:
        logger.error(f"Öneriler alınırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Öneriler alınamadı")

@app.get("/api/market/search")
async def search_stocks(query: str):
    """
    Hisse senedi araması yapar. Mock veri kullanır.
    """
    try:
        results = []
        query = query.lower()
        
        # Symbol ve name için ayrı ayrı kontrol et
        for symbol, data in TURKISH_STOCKS.items():
            clean_symbol = symbol.replace('.IS', '')  # .IS uzantısını kaldır
            if (query in clean_symbol.lower() or 
                query in data['name'].lower()):
                results.append(MarketSummary(
                    symbol=clean_symbol,
                    name=data['name'],
                    price=data['price'],
                    change=data['change'],
                    volume=data['volume']
                ))
        
        # Sonuçları alfabetik sırala
        results.sort(key=lambda x: x.symbol)
        return results
    except Exception as e:
        logger.error(f"Hisse senedi araması yapılırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Arama yapılamadı")

@app.get("/api/market/stock/{symbol}")
async def get_stock_data(symbol: str):
    """
    Belirli bir hisse senedinin verilerini döndürür. Mock veri kullanır.
    """
    try:
        symbol_with_is = f"{symbol.upper()}.IS"
        if symbol_with_is in TURKISH_STOCKS:
            data = TURKISH_STOCKS[symbol_with_is]
            return MarketSummary(
                symbol=symbol.upper(),
                name=data['name'],
                price=data['price'],
                change=data['change'],
                volume=data['volume']
            )
        raise HTTPException(status_code=404, detail="Hisse senedi bulunamadı")
    except Exception as e:
        logger.error(f"Hisse senedi verisi alınırken hata: {symbol} - {str(e)}")
        raise HTTPException(status_code=500, detail="Hisse senedi verisi alınamadı")

@app.get("/api/market/analyze/{symbol}")
async def analyze_stock_turkish(symbol: str):
    """
    Belirli bir hisse senedinin teknik analizini yapar. Mock veri kullanır.
    """
    try:
        symbol_with_is = f"{symbol.upper()}.IS"
        if symbol_with_is in TURKISH_STOCKS:
            data = TURKISH_STOCKS[symbol_with_is]
            # Basit teknik analiz
            stock = yf.Ticker(symbol_with_is)
            hist = stock.history(period="1mo")
            
            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            current_price = hist['Close'].iloc[-1]
            
            analysis = {
                "price": current_price,
                "sma_20": sma_20,
                "sma_50": sma_50,
                "trend": "Yükseliş" if sma_20 > sma_50 else "Düşüş",
                "strength": abs(sma_20 - sma_50) / sma_50 * 100,
            }
            
            return analysis
        raise HTTPException(status_code=404, detail="Hisse senedi bulunamadı")
    except Exception as e:
        logger.error(f"Hisse senedi analizi yapılırken hata: {symbol} - {str(e)}")
        raise HTTPException(status_code=500, detail="Hisse senedi analizi yapılamadı")

@app.get("/api/market/predict/{symbol}")
async def predict_stock_turkish(symbol: str):
    """
    Belirli bir hisse senedinin fiyatını öngörür. Mock veri kullanır.
    """
    try:
        symbol_with_is = f"{symbol.upper()}.IS"
        if symbol_with_is in TURKISH_STOCKS:
            data = TURKISH_STOCKS[symbol_with_is]
            # Basit bir tahmin modeli
            stock = yf.Ticker(symbol_with_is)
            hist = stock.history(period="1mo")
            
            last_price = hist['Close'].iloc[-1]
            avg_return = hist['Close'].pct_change().mean()
            std_return = hist['Close'].pct_change().std()
            
            # Monte Carlo simulasyonu
            n_simulations = 1000
            n_days = 30
            
            simulation_df = pd.DataFrame()
            for x in range(n_simulations):
                count = 0
                price_series = []
                price = last_price
                
                for y in range(n_days):
                    price = price * (1 + np.random.normal(avg_return, std_return))
                    price_series.append(price)
                    count += 1
                    
                simulation_df[x] = price_series
            
            prediction = {
                "current_price": last_price,
                "predicted_mean": simulation_df.iloc[-1].mean(),
                "predicted_high": simulation_df.iloc[-1].quantile(0.95),
                "predicted_low": simulation_df.iloc[-1].quantile(0.05),
                "confidence": 0.7,
            }
            
            return prediction
        raise HTTPException(status_code=404, detail="Hisse senedi bulunamadı")
    except Exception as e:
        logger.error(f"Hisse senedi öngörüsü yapılırken hata: {symbol} - {str(e)}")
        raise HTTPException(status_code=500, detail="Hisse senedi öngörüsü yapılamadı")

@app.post("/api/portfolio/optimize")
async def optimize_portfolio(request: PortfolioOptimizationRequest):
    """
    Portföy optimizasyonu yapar.
    """
    try:
        # Hisse senetleri verilerini al
        stock_data = {}
        for symbol in request.symbols:
            symbol_with_is = f"{symbol.upper()}.IS"
            if symbol_with_is in TURKISH_STOCKS:
                data = TURKISH_STOCKS[symbol_with_is]
                stock_data[symbol] = pd.DataFrame({
                    'price': [data['price']],
                    'change': [data['change']],
                    'volume': [data['volume']]
                })
        
        # Portföy optimizasyonu yap
        optimization_result = {
            "optimized_portfolio": stock_data,
            "risk_profile": request.risk_profile,
            "constraints": request.constraints
        }
        
        return {
            "success": True,
            "data": optimization_result
        }
    except Exception as e:
        logger.error(f"Portföy optimizasyonu yapılırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Portföy optimizasyonu yapılamadı")

@app.get("/api/portfolio", response_model=Portfolio)
async def get_portfolio():
    """
    Kullanıcının portföyünü döndürür
    """
    try:
        # TODO: Gerçek kullanıcı ID'sini auth'dan al
        user_id = 1
        if user_id in MOCK_PORTFOLIO:
            return MOCK_PORTFOLIO[user_id]
        raise HTTPException(status_code=404, detail="Portföy bulunamadı")
    except Exception as e:
        logger.error(f"Portföy bilgisi alınırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Portföy bilgisi alınamadı")

@app.post("/api/portfolio/add")
async def add_to_portfolio(request: AddToPortfolioRequest):
    """
    Portföye yeni hisse senedi ekler
    """
    try:
        # TODO: Gerçek kullanıcı ID'sini auth'dan al
        user_id = 1
        
        if user_id not in MOCK_PORTFOLIO:
            raise HTTPException(status_code=404, detail="Portföy bulunamadı")
            
        portfolio = MOCK_PORTFOLIO[user_id]
        
        # Hisse senedini bul
        symbol_with_is = f"{request.symbol.upper()}.IS"
        if symbol_with_is not in TURKISH_STOCKS:
            raise HTTPException(status_code=404, detail="Hisse senedi bulunamadı")
            
        stock_data = TURKISH_STOCKS[symbol_with_is]
        
        # Portföyde var mı kontrol et
        existing_stock = next(
            (s for s in portfolio["stocks"] if s["symbol"] == request.symbol),
            None
        )
        
        if existing_stock:
            # Mevcut hisseyi güncelle
            total_quantity = existing_stock["quantity"] + request.quantity
            total_value = total_quantity * request.price
            existing_stock.update({
                "quantity": total_quantity,
                "averagePrice": (existing_stock["averagePrice"] * existing_stock["quantity"] + 
                               request.price * request.quantity) / total_quantity,
                "currentPrice": stock_data["price"],
                "totalValue": total_value,
                "profit": total_value - (total_quantity * existing_stock["averagePrice"]),
                "profitPercentage": ((stock_data["price"] / existing_stock["averagePrice"]) - 1) * 100
            })
        else:
            # Yeni hisse ekle
            total_value = request.quantity * request.price
            portfolio["stocks"].append({
                "symbol": request.symbol,
                "name": stock_data["name"],
                "quantity": request.quantity,
                "averagePrice": request.price,
                "currentPrice": stock_data["price"],
                "totalValue": total_value,
                "profit": total_value - (request.quantity * request.price),
                "profitPercentage": ((stock_data["price"] / request.price) - 1) * 100
            })
            
        # Portföy değerlerini güncelle
        portfolio["totalValue"] = sum(s["totalValue"] for s in portfolio["stocks"])
        portfolio["dailyChange"] = sum(s["profitPercentage"] for s in portfolio["stocks"]) / len(portfolio["stocks"])
        portfolio["lastUpdated"] = datetime.now().isoformat()
        
        return {"success": True, "portfolio": portfolio}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portföye ekleme yapılırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Portföye ekleme yapılamadı")

@app.delete("/api/portfolio/remove/{symbol}")
async def remove_from_portfolio(symbol: str):
    """
    Portföyden hisse senedi çıkarır
    """
    try:
        # TODO: Gerçek kullanıcı ID'sini auth'dan al
        user_id = 1
        
        if user_id not in MOCK_PORTFOLIO:
            raise HTTPException(status_code=404, detail="Portföy bulunamadı")
            
        portfolio = MOCK_PORTFOLIO[user_id]
        
        # Hisseyi bul ve çıkar
        portfolio["stocks"] = [s for s in portfolio["stocks"] if s["symbol"] != symbol]
        
        # Portföy değerlerini güncelle
        if portfolio["stocks"]:
            portfolio["totalValue"] = sum(s["totalValue"] for s in portfolio["stocks"])
            portfolio["dailyChange"] = sum(s["profitPercentage"] for s in portfolio["stocks"]) / len(portfolio["stocks"])
        else:
            portfolio["totalValue"] = 0
            portfolio["dailyChange"] = 0
            
        portfolio["lastUpdated"] = datetime.now().isoformat()
        
        return {"success": True, "portfolio": portfolio}
    except Exception as e:
        logger.error(f"Portföyden hisse çıkarılırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Portföyden hisse çıkarılamadı")

@app.put("/api/portfolio/update/{symbol}")
async def update_quantity(symbol: str, quantity: int):
    """
    Portföydeki hisse senedi miktarını günceller
    """
    try:
        # TODO: Gerçek kullanıcı ID'sini auth'dan al
        user_id = 1
        
        if user_id not in MOCK_PORTFOLIO:
            raise HTTPException(status_code=404, detail="Portföy bulunamadı")
            
        portfolio = MOCK_PORTFOLIO[user_id]
        
        # Hisseyi bul
        stock = next((s for s in portfolio["stocks"] if s["symbol"] == symbol), None)
        if not stock:
            raise HTTPException(status_code=404, detail="Hisse senedi bulunamadı")
            
        # Miktarı güncelle
        stock["quantity"] = quantity
        stock["totalValue"] = quantity * stock["currentPrice"]
        stock["profit"] = stock["totalValue"] - (quantity * stock["averagePrice"])
        stock["profitPercentage"] = ((stock["currentPrice"] / stock["averagePrice"]) - 1) * 100
        
        # Portföy değerlerini güncelle
        portfolio["totalValue"] = sum(s["totalValue"] for s in portfolio["stocks"])
        portfolio["dailyChange"] = sum(s["profitPercentage"] for s in portfolio["stocks"]) / len(portfolio["stocks"])
        portfolio["lastUpdated"] = datetime.now().isoformat()
        
        return {"success": True, "portfolio": portfolio}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hisse miktarı güncellenirken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Hisse miktarı güncellenemedi")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PYTHON_API_PORT)