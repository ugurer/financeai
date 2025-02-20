import { Request, Response } from 'express';
import { getRepository } from 'typeorm';
import { Portfolio } from '../entities/Portfolio';
import { PortfolioHolding } from '../entities/PortfolioHolding';
import { Transaction } from '../entities/Transaction';
import { fetchStockPrice } from '../services/stockService';

export class PortfolioController {
  private portfolioRepository = getRepository(Portfolio);
  private holdingRepository = getRepository(PortfolioHolding);
  private transactionRepository = getRepository(Transaction);

  getSummary = async (req: Request, res: Response): Promise<Response> => {
    try {
      const userId = req.user.id;

      const portfolio = await this.portfolioRepository.findOne({
        where: { userId },
        relations: ['holdings'],
      });

      if (!portfolio) {
        return res.status(404).json({ message: 'Portfolio not found' });
      }

      // Calculate total value and daily changes
      let totalValue = portfolio.cashBalance;
      let previousDayValue = portfolio.cashBalance;
      
      for (const holding of portfolio.holdings) {
        const currentPrice = await fetchStockPrice(holding.symbol);
        const holdingValue = holding.quantity * currentPrice.current;
        const previousDayHoldingValue = holding.quantity * currentPrice.previousClose;
        
        totalValue += holdingValue;
        previousDayValue += previousDayHoldingValue;
      }

      const dailyChange = totalValue - previousDayValue;
      const dailyChangePercentage = (dailyChange / previousDayValue) * 100;

      return res.json({
        totalValue,
        dailyChange,
        dailyChangePercentage,
        cashBalance: portfolio.cashBalance,
      });
    } catch (error) {
      console.error('Portfolio summary error:', error);
      return res.status(500).json({ message: 'Internal server error' });
    }
  };

  getHoldings = async (req: Request, res: Response): Promise<Response> => {
    try {
      const userId = req.user.id;

      const holdings = await this.holdingRepository.find({
        where: { portfolio: { userId } },
      });

      // Fetch current prices for all holdings
      const holdingsWithCurrentPrice = await Promise.all(
        holdings.map(async (holding) => {
          const price = await fetchStockPrice(holding.symbol);
          const currentValue = holding.quantity * price.current;
          const profitLoss = currentValue - (holding.quantity * holding.averagePrice);
          
          return {
            ...holding,
            currentPrice: price.current,
            currentValue,
            profitLoss,
            profitLossPercentage: (profitLoss / (holding.quantity * holding.averagePrice)) * 100,
          };
        })
      );

      return res.json(holdingsWithCurrentPrice);
    } catch (error) {
      console.error('Holdings fetch error:', error);
      return res.status(500).json({ message: 'Internal server error' });
    }
  };

  executeTransaction = async (req: Request, res: Response): Promise<Response> => {
    try {
      const userId = req.user.id;
      const { symbol, type, quantity, price } = req.body;

      const portfolio = await this.portfolioRepository.findOne({
        where: { userId },
        relations: ['holdings'],
      });

      if (!portfolio) {
        return res.status(404).json({ message: 'Portfolio not found' });
      }

      const totalAmount = quantity * price;

      // Validate transaction
      if (type === 'BUY') {
        if (portfolio.cashBalance < totalAmount) {
          return res.status(400).json({ message: 'Insufficient funds' });
        }
      } else if (type === 'SELL') {
        const holding = portfolio.holdings.find(h => h.symbol === symbol);
        if (!holding || holding.quantity < quantity) {
          return res.status(400).json({ message: 'Insufficient holdings' });
        }
      }

      // Create transaction
      const transaction = this.transactionRepository.create({
        portfolio,
        symbol,
        transactionType: type,
        quantity,
        price,
        totalAmount,
      });

      // Update portfolio cash balance
      portfolio.cashBalance += type === 'SELL' ? totalAmount : -totalAmount;

      // Update or create holding
      let holding = portfolio.holdings.find(h => h.symbol === symbol);
      if (holding) {
        if (type === 'BUY') {
          const newQuantity = holding.quantity + quantity;
          holding.averagePrice = ((holding.quantity * holding.averagePrice) + totalAmount) / newQuantity;
          holding.quantity = newQuantity;
        } else {
          holding.quantity -= quantity;
          if (holding.quantity === 0) {
            await this.holdingRepository.remove(holding);
          }
        }
      } else if (type === 'BUY') {
        holding = this.holdingRepository.create({
          portfolio,
          symbol,
          quantity,
          averagePrice: price,
        });
      }

      // Save all changes
      await this.portfolioRepository.save(portfolio);
      if (holding && holding.quantity > 0) {
        await this.holdingRepository.save(holding);
      }
      await this.transactionRepository.save(transaction);

      return res.json({
        message: 'Transaction executed successfully',
        transaction,
        updatedPortfolio: {
          cashBalance: portfolio.cashBalance,
          holding: holding || null,
        },
      });
    } catch (error) {
      console.error('Transaction error:', error);
      return res.status(500).json({ message: 'Internal server error' });
    }
  };
}
