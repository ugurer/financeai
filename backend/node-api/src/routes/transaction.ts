import express, { Request, Response } from 'express';
import { getRepository } from 'typeorm';
import { Transaction } from '../models/Transaction';
import { Portfolio } from '../models/Portfolio';
import { PortfolioHolding } from '../models/PortfolioHolding';
import { verifyToken } from '../middleware/auth';

interface AuthRequest extends Request {
    user?: {
        userId: number;
        email?: string;
    };
}

const router = express.Router();

// Yeni işlem ekleme
router.post('/:portfolioId', verifyToken, async (req: AuthRequest, res: Response) => {
    try {
        const userId = req.user?.userId;
        const portfolioId = parseInt(req.params.portfolioId);
        const { symbol, transaction_type, quantity, price } = req.body;

        if (!userId) {
            return res.status(401).json({ error: 'Kullanıcı kimliği bulunamadı' });
        }

        // Portföyü kontrol et
        const portfolioRepository = getRepository(Portfolio);
        const portfolio = await portfolioRepository.findOne({
            where: { id: portfolioId, user_id: userId }
        });

        if (!portfolio) {
            return res.status(404).json({ error: 'Portföy bulunamadı' });
        }

        const total_amount = quantity * price;

        // İşlem tipine göre kontroller
        if (transaction_type === 'buy') {
            if (portfolio.cash_balance < total_amount) {
                return res.status(400).json({ error: 'Yetersiz bakiye' });
            }
        } else {
            const holdingRepository = getRepository(PortfolioHolding);
            const holding = await holdingRepository.findOne({
                where: { portfolio_id: portfolioId, symbol }
            });

            if (!holding || holding.quantity < quantity) {
                return res.status(400).json({ error: 'Yetersiz hisse miktarı' });
            }
        }

        // İşlemi kaydet
        const transactionRepository = getRepository(Transaction);
        const transaction = transactionRepository.create({
            portfolio_id: portfolioId,
            symbol,
            transaction_type,
            quantity,
            price,
            total_amount
        });

        await transactionRepository.save(transaction);

        // Portföy ve holding güncelleme
        if (transaction_type === 'buy') {
            portfolio.cash_balance -= total_amount;
            await portfolioRepository.save(portfolio);

            const holdingRepository = getRepository(PortfolioHolding);
            let holding = await holdingRepository.findOne({
                where: { portfolio_id: portfolioId, symbol }
            });

            if (holding) {
                holding.quantity += quantity;
                holding.average_price = ((holding.quantity * holding.average_price) + total_amount) / (holding.quantity + quantity);
                await holdingRepository.save(holding);
            } else {
                holding = holdingRepository.create({
                    portfolio_id: portfolioId,
                    symbol,
                    quantity,
                    average_price: price
                });
                await holdingRepository.save(holding);
            }
        } else {
            portfolio.cash_balance += total_amount;
            await portfolioRepository.save(portfolio);

            const holdingRepository = getRepository(PortfolioHolding);
            const holding = await holdingRepository.findOne({
                where: { portfolio_id: portfolioId, symbol }
            });

            if (holding) {
                if (holding.quantity === quantity) {
                    await holdingRepository.remove(holding);
                } else {
                    holding.quantity -= quantity;
                    await holdingRepository.save(holding);
                }
            }
        }

        res.status(201).json(transaction);
    } catch (error) {
        console.error('İşlem hatası:', error);
        res.status(500).json({ error: 'İşlem gerçekleştirilemedi' });
    }
});

// İşlem geçmişini getirme
router.get('/:portfolioId', verifyToken, async (req: AuthRequest, res: Response) => {
    try {
        const userId = req.user?.userId;
        const portfolioId = parseInt(req.params.portfolioId);

        if (!userId) {
            return res.status(401).json({ error: 'Kullanıcı kimliği bulunamadı' });
        }

        // Portföyü kontrol et
        const portfolioRepository = getRepository(Portfolio);
        const portfolio = await portfolioRepository.findOne({
            where: { id: portfolioId, user_id: userId }
        });

        if (!portfolio) {
            return res.status(404).json({ error: 'Portföy bulunamadı' });
        }

        // İşlemleri getir
        const transactionRepository = getRepository(Transaction);
        const transactions = await transactionRepository.find({
            where: { portfolio_id: portfolioId },
            order: { transaction_date: 'DESC' }
        });

        res.json(transactions);
    } catch (error) {
        console.error('İşlem geçmişi getirme hatası:', error);
        res.status(500).json({ error: 'İşlem geçmişi alınamadı' });
    }
});

export default router; 