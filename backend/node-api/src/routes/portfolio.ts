import express, { Request, Response, NextFunction } from 'express';
import { getRepository } from 'typeorm';
import jwt from 'jsonwebtoken';

const router = express.Router();

// Custom request interface
interface AuthRequest extends Request {
    user?: {
        userId: number;
    };
}

// Middleware to verify JWT token
const verifyToken = (req: AuthRequest, res: Response, next: NextFunction) => {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
        return res.status(401).json({ error: 'Token bulunamadı' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key') as { userId: number };
        req.user = decoded;
        next();
    } catch (error) {
        return res.status(401).json({ error: 'Geçersiz token' });
    }
};

// Portföy oluşturma
router.post('/', verifyToken, async (req: AuthRequest, res: Response) => {
    try {
        const { name, initialBalance } = req.body;
        const userId = req.user?.userId;

        if (!userId) {
            res.status(401).json({ error: 'Kullanıcı kimliği bulunamadı' });
            return;
        }

        const portfolio = await getRepository('portfolios').save({
            user_id: userId,
            name,
            total_value: initialBalance,
            cash_balance: initialBalance
        });

        res.status(201).json(portfolio);
    } catch (error) {
        console.error('Portföy oluşturma hatası:', error);
        res.status(500).json({ error: 'Portföy oluşturulurken bir hata oluştu.' });
    }
});

// Kullanıcının portföylerini getirme
router.get('/', verifyToken, async (req: AuthRequest, res: Response) => {
    try {
        const userId = req.user?.userId;

        if (!userId) {
            res.status(401).json({ error: 'Kullanıcı kimliği bulunamadı' });
            return;
        }

        const portfolios = await getRepository('portfolios').find({
            where: { user_id: userId }
        });

        res.json(portfolios);
    } catch (error) {
        console.error('Portföy listeleme hatası:', error);
        res.status(500).json({ error: 'Portföyler listelenirken bir hata oluştu.' });
    }
});

// Portföy detaylarını getirme
router.get('/:id', verifyToken, async (req: AuthRequest, res: Response) => {
    try {
        const portfolioId = parseInt(req.params.id);
        const userId = req.user?.userId;

        if (!userId) {
            res.status(401).json({ error: 'Kullanıcı kimliği bulunamadı' });
            return;
        }

        const portfolio = await getRepository('portfolios').findOne({
            where: { id: portfolioId, user_id: userId }
        });

        if (!portfolio) {
            res.status(404).json({ error: 'Portföy bulunamadı.' });
            return;
        }

        // Portföy varlıklarını getir
        const holdings = await getRepository('portfolio_holdings').find({
            where: { portfolio_id: portfolioId }
        });

        res.json({
            ...portfolio,
            holdings
        });
    } catch (error) {
        console.error('Portföy detay hatası:', error);
        res.status(500).json({ error: 'Portföy detayları alınırken bir hata oluştu.' });
    }
});

export default router; 