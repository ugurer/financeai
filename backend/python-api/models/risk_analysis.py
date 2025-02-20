import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Union

class RiskAnalysisModel:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def calculate_portfolio_risk(self, 
                               returns: List[float], 
                               weights: List[float]) -> Dict[str, Union[float, str]]:
        """
        Calculate portfolio risk metrics based on historical returns
        
        Args:
            returns: List of historical returns
            weights: Portfolio weights for each asset
            
        Returns:
            Dictionary containing risk metrics
        """
        returns_array = np.array(returns)
        weights_array = np.array(weights)
        
        # Calculate portfolio metrics
        portfolio_return = np.sum(returns_array.mean() * weights_array) * 252
        portfolio_std = np.sqrt(np.dot(weights_array.T, np.dot(np.cov(returns_array.T) * 252, weights_array)))
        sharpe_ratio = portfolio_return / portfolio_std
        
        # Determine risk level
        risk_level = self._determine_risk_level(portfolio_std)
        
        return {
            "annual_return": float(portfolio_return),
            "annual_volatility": float(portfolio_std),
            "sharpe_ratio": float(sharpe_ratio),
            "risk_level": risk_level
        }
    
    def _determine_risk_level(self, volatility: float) -> str:
        """
        Determine risk level based on portfolio volatility
        
        Args:
            volatility: Portfolio volatility
            
        Returns:
            Risk level classification
        """
        if volatility < 0.15:
            return "low"
        elif volatility < 0.25:
            return "medium"
        else:
            return "high"
    
    def optimize_portfolio(self, 
                         returns: List[float], 
                         target_risk: str) -> Dict[str, List[float]]:
        """
        Optimize portfolio weights based on target risk level
        
        Args:
            returns: Historical returns
            target_risk: Desired risk level (low/medium/high)
            
        Returns:
            Dictionary containing optimized weights
        """
        risk_targets = {
            "low": 0.12,
            "medium": 0.20,
            "high": 0.30
        }
        
        target_volatility = risk_targets[target_risk]
        num_assets = len(returns)
        
        # Simple optimization using equal weights as starting point
        initial_weights = np.array([1/num_assets] * num_assets)
        
        # Adjust weights based on target volatility
        current_risk = self.calculate_portfolio_risk(returns, initial_weights)["annual_volatility"]
        adjustment_factor = target_volatility / current_risk
        
        optimized_weights = initial_weights * adjustment_factor
        optimized_weights = optimized_weights / np.sum(optimized_weights)  # Normalize weights
        
        return {
            "weights": optimized_weights.tolist()
        }
