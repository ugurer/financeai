import express, { Response } from 'express';
import { getRepository } from 'typeorm';
import { RiskAssessment } from '../models/RiskAssessment';
import { verifyToken } from '../middleware/auth';
import { AuthRequest } from '../types/auth';

const router = express.Router();

// Risk değerlendirme formu gönderme
router.post('/', verifyToken, async (req: AuthRequest, res: Response) => {
    try {
        const { risk_level, investment_duration, risk_tolerance, financial_goals } = req.body;
        const userId = req.user?.userId;

        if (!userId) {
            return res.status(401).json({ error: 'Kullanıcı kimliği bulunamadı' });
        }

        const riskRepository = getRepository(RiskAssessment);
        const assessment = riskRepository.create({
            user_id: userId,
            risk_level,
            investment_duration,
            risk_tolerance,
            financial_goals
        });

        await riskRepository.save(assessment);
        res.status(201).json(assessment);
    } catch (error) {
        console.error('Risk değerlendirme hatası:', error);
        res.status(500).json({ error: 'Risk değerlendirme kaydedilemedi' });
    }
});

// Kullanıcının risk profilini getirme
router.get('/', verifyToken, async (req: AuthRequest, res: Response) => {
    try {
        const userId = req.user?.userId;

        if (!userId) {
            return res.status(401).json({ error: 'Kullanıcı kimliği bulunamadı' });
        }

        const riskRepository = getRepository(RiskAssessment);
        const assessment = await riskRepository.findOne({
            where: { user_id: userId },
            order: { created_at: 'DESC' }
        });

        if (!assessment) {
            return res.status(404).json({ error: 'Risk değerlendirme bulunamadı' });
        }

        res.json(assessment);
    } catch (error) {
        console.error('Risk profili getirme hatası:', error);
        res.status(500).json({ error: 'Risk profili alınamadı' });
    }
});

// Risk profilini güncelleme
router.put('/', verifyToken, async (req: AuthRequest, res: Response) => {
    try {
        const userId = req.user?.userId;
        const { risk_level, investment_duration, risk_tolerance, financial_goals } = req.body;

        if (!userId) {
            return res.status(401).json({ error: 'Kullanıcı kimliği bulunamadı' });
        }

        const riskRepository = getRepository(RiskAssessment);
        const assessment = await riskRepository.findOne({
            where: { user_id: userId },
            order: { created_at: 'DESC' }
        });

        if (!assessment) {
            return res.status(404).json({ error: 'Risk değerlendirme bulunamadı' });
        }

        assessment.risk_level = risk_level;
        assessment.investment_duration = investment_duration;
        assessment.risk_tolerance = risk_tolerance;
        assessment.financial_goals = financial_goals;

        await riskRepository.save(assessment);
        res.json(assessment);
    } catch (error) {
        console.error('Risk profili güncelleme hatası:', error);
        res.status(500).json({ error: 'Risk profili güncellenemedi' });
    }
});

export default router; 