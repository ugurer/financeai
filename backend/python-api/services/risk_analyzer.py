from typing import Dict, List, Optional
import numpy as np
from sklearn.preprocessing import StandardScaler
from pydantic import BaseModel

class RiskProfile(BaseModel):
    risk_level: str
    investment_duration: int
    risk_tolerance: int
    financial_goals: Optional[List[str]]

class RiskAnalyzer:
    def __init__(self):
        self.risk_levels = {
            'low': {'max_volatility': 0.15, 'max_drawdown': 0.10},
            'medium': {'max_volatility': 0.25, 'max_drawdown': 0.20},
            'high': {'max_volatility': 0.35, 'max_drawdown': 0.30}
        }

    def analyze_portfolio_risk(self, portfolio_data: Dict) -> Dict:
        """
        Portföy risk analizi yapar
        """
        # Portföy getirilerini hesapla
        returns = self._calculate_returns(portfolio_data['historical_prices'])
        
        # Risk metriklerini hesapla
        volatility = self._calculate_volatility(returns)
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        max_drawdown = self._calculate_max_drawdown(portfolio_data['historical_prices'])
        
        # Beta ve alfa hesapla
        market_correlation = self._calculate_market_correlation(returns, portfolio_data['market_returns'])
        
        return {
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'market_correlation': market_correlation,
            'risk_metrics': {
                'var_95': self._calculate_var(returns, 0.95),
                'cvar_95': self._calculate_cvar(returns, 0.95)
            }
        }

    def get_risk_recommendations(self, risk_profile: RiskProfile, portfolio_risk: Dict) -> List[Dict]:
        """
        Risk profiline göre öneriler oluşturur
        """
        recommendations = []
        risk_limits = self.risk_levels[risk_profile.risk_level]

        # Volatilite kontrolü
        if portfolio_risk['volatility'] > risk_limits['max_volatility']:
            recommendations.append({
                'type': 'warning',
                'message': 'Portföy volatilitesi risk limitinizin üzerinde',
                'action': 'Daha düşük volatiliteli varlıklara geçiş yapmanızı öneririz'
            })

        # Drawdown kontrolü
        if portfolio_risk['max_drawdown'] > risk_limits['max_drawdown']:
            recommendations.append({
                'type': 'warning',
                'message': 'Maksimum kayıp oranı risk limitinizin üzerinde',
                'action': 'Stop-loss emirleri kullanmanızı ve portföy çeşitlendirmenizi öneririz'
            })

        # Sharpe ratio değerlendirmesi
        if portfolio_risk['sharpe_ratio'] < 1:
            recommendations.append({
                'type': 'suggestion',
                'message': 'Risk-getiri oranınız optimal değil',
                'action': 'Portföy optimizasyonu yapmanızı öneririz'
            })

        return recommendations

    def _calculate_returns(self, prices: List[float]) -> np.ndarray:
        """Günlük getirileri hesaplar"""
        return np.diff(np.log(prices))

    def _calculate_volatility(self, returns: np.ndarray) -> float:
        """Yıllık volatiliteyi hesaplar"""
        return np.std(returns) * np.sqrt(252)

    def _calculate_sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Sharpe oranını hesaplar"""
        excess_returns = returns - risk_free_rate/252
        return np.sqrt(252) * np.mean(excess_returns) / np.std(returns)

    def _calculate_max_drawdown(self, prices: List[float]) -> float:
        """Maksimum düşüş oranını hesaplar"""
        peak = prices[0]
        max_drawdown = 0
        
        for price in prices:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak
            max_drawdown = max(max_drawdown, drawdown)
            
        return max_drawdown

    def _calculate_market_correlation(self, returns: np.ndarray, market_returns: np.ndarray) -> float:
        """Piyasa korelasyonunu hesaplar"""
        return np.corrcoef(returns, market_returns)[0, 1]

    def _calculate_var(self, returns: np.ndarray, confidence_level: float) -> float:
        """Value at Risk hesaplar"""
        return np.percentile(returns, (1 - confidence_level) * 100)

    def _calculate_cvar(self, returns: np.ndarray, confidence_level: float) -> float:
        """Conditional Value at Risk hesaplar"""
        var = self._calculate_var(returns, confidence_level)
        return np.mean(returns[returns <= var])
