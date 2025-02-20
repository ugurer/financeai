import { getRepository } from 'typeorm';
import axios from 'axios';

interface PortfolioHolding {
    symbol: string;
    quantity: number;
    averagePrice: number;
    currentPrice: number;
    totalValue: number;
    profitLoss: number;
    profitLossPercentage: number;
}

interface Portfolio {
    id: number;
    userId: number;
    name: string;
    totalValue: number;
    cashBalance: number;
    holdings: PortfolioHolding[];
    dailyChange: number;
    dailyChangePercentage: number;
}

interface PortfolioEntity {
    id: number;
    user_id: number;
    name: string;
    total_value: number;
    cash_balance: number;
}

export class PortfolioService {
    public static async createPortfolio(userId: number, name: string, initialBalance: number): Promise<Portfolio> {
        const portfolioRepository = getRepository('portfolios');
        
        const portfolio = await portfolioRepository.save({
            user_id: userId,
            name,
            total_value: initialBalance,
            cash_balance: initialBalance
        }) as PortfolioEntity;

        return {
            id: portfolio.id,
            userId: portfolio.user_id,
            name: portfolio.name,
            totalValue: portfolio.total_value,
            cashBalance: portfolio.cash_balance,
            holdings: [],
            dailyChange: 0,
            dailyChangePercentage: 0
        };
    }

    public static async getPortfolio(portfolioId: number, userId: number): Promise<Portfolio> {
        const portfolioRepository = getRepository('portfolios');
        const holdingsRepository = getRepository('portfolio_holdings');

        const portfolio = await portfolioRepository.findOne({
            where: { id: portfolioId, user_id: userId }
        }) as PortfolioEntity | undefined;

        if (!portfolio) {
            throw new Error('Portföy bulunamadı.');
        }

        const holdings = await holdingsRepository.find({
            where: { portfolio_id: portfolioId }
        });

        // Güncel fiyatları al
        const holdingsWithCurrentPrices = await Promise.all(
            holdings.map(async (holding) => {
                const currentPrice = await this.getCurrentPrice(holding.symbol);
                const totalValue = holding.quantity * currentPrice;
                const profitLoss = totalValue - (holding.quantity * holding.average_price);
                const profitLossPercentage = (profitLoss / (holding.quantity * holding.average_price)) * 100;

                return {
                    symbol: holding.symbol,
                    quantity: holding.quantity,
                    averagePrice: holding.average_price,
                    currentPrice,
                    totalValue,
                    profitLoss,
                    profitLossPercentage
                };
            })
        );

        // Portföy değerlerini hesapla
        const totalValue = holdingsWithCurrentPrices.reduce(
            (sum, holding) => sum + holding.totalValue,
            portfolio.cash_balance
        );

        const previousTotalValue = portfolio.total_value;
        const dailyChange = totalValue - previousTotalValue;
        const dailyChangePercentage = (dailyChange / previousTotalValue) * 100;

        // Portföy değerini güncelle
        await portfolioRepository.update(portfolioId, { total_value: totalValue });

        return {
            id: portfolio.id,
            userId: portfolio.user_id,
            name: portfolio.name,
            totalValue,
            cashBalance: portfolio.cash_balance,
            holdings: holdingsWithCurrentPrices,
            dailyChange,
            dailyChangePercentage
        };
    }

    public static async addTransaction(
        portfolioId: number,
        userId: number,
        symbol: string,
        quantity: number,
        price: number,
        type: 'buy' | 'sell'
    ): Promise<void> {
        const portfolioRepository = getRepository('portfolios');
        const holdingsRepository = getRepository('portfolio_holdings');
        const transactionsRepository = getRepository('transactions');

        const portfolio = await portfolioRepository.findOne({
            where: { id: portfolioId, user_id: userId }
        });

        if (!portfolio) {
            throw new Error('Portföy bulunamadı.');
        }

        const totalAmount = quantity * price;

        if (type === 'buy') {
            if (portfolio.cash_balance < totalAmount) {
                throw new Error('Yetersiz bakiye.');
            }

            // Mevcut holding'i kontrol et
            let holding = await holdingsRepository.findOne({
                where: { portfolio_id: portfolioId, symbol }
            });

            if (holding) {
                // Ortalama fiyatı güncelle
                const newTotalQuantity = holding.quantity + quantity;
                const newAveragePrice = (
                    (holding.quantity * holding.average_price) + (quantity * price)
                ) / newTotalQuantity;

                await holdingsRepository.update(holding.id, {
                    quantity: newTotalQuantity,
                    average_price: newAveragePrice
                });
            } else {
                // Yeni holding oluştur
                await holdingsRepository.save({
                    portfolio_id: portfolioId,
                    symbol,
                    quantity,
                    average_price: price
                });
            }

            // Nakit bakiyeyi güncelle
            await portfolioRepository.update(portfolioId, {
                cash_balance: portfolio.cash_balance - totalAmount
            });
        } else { // sell
            const holding = await holdingsRepository.findOne({
                where: { portfolio_id: portfolioId, symbol }
            });

            if (!holding || holding.quantity < quantity) {
                throw new Error('Yetersiz hisse miktarı.');
            }

            if (holding.quantity === quantity) {
                // Holding'i sil
                await holdingsRepository.delete(holding.id);
            } else {
                // Miktarı güncelle
                await holdingsRepository.update(holding.id, {
                    quantity: holding.quantity - quantity
                });
            }

            // Nakit bakiyeyi güncelle
            await portfolioRepository.update(portfolioId, {
                cash_balance: portfolio.cash_balance + totalAmount
            });
        }

        // İşlemi kaydet
        await transactionsRepository.save({
            portfolio_id: portfolioId,
            symbol,
            transaction_type: type,
            quantity,
            price,
            total_amount: totalAmount
        });
    }

    private static async getCurrentPrice(symbol: string): Promise<number> {
        try {
            // TODO: Gerçek API entegrasyonu
            // Şimdilik rastgele fiyat döndür
            return Math.random() * 1000;
        } catch (error) {
            console.error(`Fiyat alınamadı (${symbol}):`, error);
            throw new Error('Fiyat bilgisi alınamadı.');
        }
    }
} 