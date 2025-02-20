import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple

class PortfolioOptimizer:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def calculate_portfolio_metrics(self, holdings: List[Dict]) -> Dict:
        """
        Portföy metriklerini hesaplar
        """
        try:
            # Varlık verilerini topla
            symbols = [h['symbol'] for h in holdings]
            weights = np.array([h['quantity'] * h['average_price'] for h in holdings])
            weights = weights / np.sum(weights)
            
            # Risk ve getiri hesaplamaları
            returns = self._calculate_returns(symbols)
            portfolio_return = np.sum(returns.mean() * weights) * 252
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            
            # Çeşitlendirme skoru
            diversification_score = self._calculate_diversification_score(holdings)
            
            return {
                'annual_return': float(portfolio_return),
                'annual_risk': float(portfolio_risk),
                'sharpe_ratio': float(portfolio_return / portfolio_risk),
                'diversification_score': float(diversification_score)
            }
        except Exception as e:
            print(f"Portföy metrikleri hesaplanırken hata: {str(e)}")
            return {}
    
    def generate_recommendations(self, holdings: List[Dict], risk_profile: str) -> List[Dict]:
        """
        Portföy önerileri oluşturur
        """
        try:
            current_allocation = self._analyze_current_allocation(holdings)
            target_allocation = self._get_target_allocation(risk_profile)
            
            recommendations = []
            for asset_class, target in target_allocation.items():
                current = current_allocation.get(asset_class, 0)
                if current < target - 0.05:  # %5 tolerans
                    recommendations.append({
                        'action': 'buy',
                        'asset_class': asset_class,
                        'reason': f'{asset_class} ağırlığı hedef dağılımın altında'
                    })
                elif current > target + 0.05:
                    recommendations.append({
                        'action': 'sell',
                        'asset_class': asset_class,
                        'reason': f'{asset_class} ağırlığı hedef dağılımın üstünde'
                    })
            
            return recommendations
        except Exception as e:
            print(f"Öneriler oluşturulurken hata: {str(e)}")
            return []
    
    def _calculate_returns(self, symbols: List[str]) -> pd.DataFrame:
        """
        Hisse senetleri için getiri hesaplar
        """
        # TODO: Yahoo Finance'den geçmiş verileri çek
        # Şimdilik örnek veri kullanıyoruz
        return pd.DataFrame(np.random.normal(0.001, 0.02, (252, len(symbols))))
    
    def _calculate_diversification_score(self, holdings: List[Dict]) -> float:
        """
        Portföy çeşitlendirme skorunu hesaplar
        """
        if not holdings:
            return 0.0
            
        # Sektör bazlı çeşitlendirme
        sectors = [h.get('sector', 'Unknown') for h in holdings]
        sector_weights = pd.Series(sectors).value_counts(normalize=True)
        
        # Herfindahl endeksi
        herfindahl = np.sum(sector_weights ** 2)
        
        # 0-1 arasında normalize edilmiş skor (1 = tam çeşitlendirme)
        return 1 - herfindahl
    
    def _analyze_current_allocation(self, holdings: List[Dict]) -> Dict[str, float]:
        """
        Mevcut portföy dağılımını analiz eder
        """
        total_value = sum(h['quantity'] * h['average_price'] for h in holdings)
        allocation = {}
        
        for holding in holdings:
            asset_class = holding.get('asset_class', 'stocks')
            value = holding['quantity'] * holding['average_price']
            allocation[asset_class] = allocation.get(asset_class, 0) + value / total_value
            
        return allocation
    
    def _get_target_allocation(self, risk_profile: str) -> Dict[str, float]:
        """
        Risk profiline göre hedef dağılımı belirler
        """
        allocations = {
            'conservative': {'stocks': 0.3, 'bonds': 0.6, 'cash': 0.1},
            'moderate': {'stocks': 0.6, 'bonds': 0.3, 'cash': 0.1},
            'aggressive': {'stocks': 0.8, 'bonds': 0.15, 'cash': 0.05}
        }
        
        return allocations.get(risk_profile, allocations['moderate']) 