from typing import Dict, List
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler
from pydantic import BaseModel

class PortfolioOptimizer:
    def __init__(self):
        self.risk_weights = {
            'low': {'return': 0.2, 'risk': 0.8},
            'medium': {'return': 0.5, 'risk': 0.5},
            'high': {'return': 0.8, 'risk': 0.2}
        }

    def optimize_portfolio(self, stock_data: Dict[str, pd.DataFrame], risk_profile: str,
                         constraints: Dict = None) -> Dict:
        """
        Modern Portföy Teorisi'ne göre portföy optimizasyonu yapar
        """
        # Getirileri hesapla
        returns = self._calculate_returns(stock_data)
        
        # Kovaryans matrisini hesapla
        cov_matrix = returns.cov() * 252
        exp_returns = returns.mean() * 252

        # Optimizasyon kısıtlarını ayarla
        constraints = self._prepare_constraints(constraints)
        
        # Risk profiline göre hedef ağırlıkları belirle
        weights = self._optimize_weights(exp_returns, cov_matrix, self.risk_weights[risk_profile])

        # Portföy metriklerini hesapla
        portfolio_metrics = self._calculate_portfolio_metrics(weights, exp_returns, cov_matrix)

        return {
            'weights': dict(zip(stock_data.keys(), weights)),
            'expected_return': portfolio_metrics['return'],
            'volatility': portfolio_metrics['volatility'],
            'sharpe_ratio': portfolio_metrics['sharpe_ratio']
        }

    def _calculate_returns(self, stock_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Hisse senetleri için günlük getirileri hesaplar"""
        returns_dict = {}
        for symbol, data in stock_data.items():
            returns_dict[symbol] = np.diff(np.log(data['close']))
        return pd.DataFrame(returns_dict)

    def _prepare_constraints(self, constraints: Dict = None) -> List:
        """Optimizasyon kısıtlarını hazırlar"""
        if constraints is None:
            constraints = {}

        default_constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Ağırlıklar toplamı 1 olmalı
            {'type': 'ineq', 'fun': lambda x: x},  # Ağırlıklar pozitif olmalı
        ]

        if 'min_weight' in constraints:
            default_constraints.append(
                {'type': 'ineq', 'fun': lambda x: x - constraints['min_weight']}
            )

        if 'max_weight' in constraints:
            default_constraints.append(
                {'type': 'ineq', 'fun': lambda x: constraints['max_weight'] - x}
            )

        return default_constraints

    def _optimize_weights(self, returns: pd.Series, cov_matrix: pd.DataFrame,
                        risk_weights: Dict) -> np.ndarray:
        """Optimal portföy ağırlıklarını hesaplar"""
        n_assets = len(returns)
        init_weights = np.array([1/n_assets] * n_assets)

        def objective(weights):
            portfolio_return = np.sum(returns * weights)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # Risk-getiri trade-off'unu optimize et
            return -(risk_weights['return'] * portfolio_return - 
                    risk_weights['risk'] * portfolio_volatility)

        result = minimize(objective, init_weights,
                        method='SLSQP',
                        constraints=self._prepare_constraints())

        return result.x

    def _calculate_portfolio_metrics(self, weights: np.ndarray, returns: pd.Series,
                                  cov_matrix: pd.DataFrame) -> Dict:
        """Portföy metriklerini hesaplar"""
        portfolio_return = np.sum(returns * weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = portfolio_return / portfolio_volatility

        return {
            'return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio
        }

    def rebalance_portfolio(self, current_weights: Dict[str, float],
                          optimal_weights: Dict[str, float],
                          threshold: float = 0.05) -> List[Dict]:
        """
        Portföy rebalancing önerileri oluşturur
        """
        recommendations = []
        
        for symbol in current_weights.keys():
            current = current_weights[symbol]
            target = optimal_weights[symbol]
            diff = target - current
            
            if abs(diff) > threshold:
                action = 'buy' if diff > 0 else 'sell'
                recommendations.append({
                    'symbol': symbol,
                    'action': action,
                    'current_weight': current,
                    'target_weight': target,
                    'difference': abs(diff),
                    'message': f"{symbol} için {action.upper()} işlemi yaparak %{abs(diff)*100:.1f} "
                              f"ağırlık değişimi önerilir"
                })

        return sorted(recommendations, key=lambda x: abs(x['difference']), reverse=True)
