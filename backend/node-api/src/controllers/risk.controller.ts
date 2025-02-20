import { Request, Response } from 'express';
import { getRepository } from 'typeorm';
import { User } from '../entities/User';
import { RiskAssessment } from '../entities/RiskAssessment';
import axios from 'axios';

export class RiskController {
  private userRepository = getRepository(User);
  private riskAssessmentRepository = getRepository(RiskAssessment);
  private ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://python-api:8000';

  submitAssessment = async (req: Request, res: Response): Promise<Response> => {
    try {
      const userId = req.user.id;
      const {
        investmentDuration,
        riskTolerance,
        financialGoals,
        monthlyIncome,
        monthlyExpenses,
        existingInvestments,
        dependents,
      } = req.body;

      // Create risk assessment record
      const assessment = this.riskAssessmentRepository.create({
        userId,
        investmentDuration,
        riskTolerance,
        financialGoals,
        monthlyIncome,
        monthlyExpenses,
        existingInvestments,
        dependents,
      });

      // Call ML service for risk analysis
      const mlResponse = await axios.post(`${this.ML_SERVICE_URL}/risk/analyze`, {
        investmentDuration,
        riskTolerance,
        monthlyIncome,
        monthlyExpenses,
        existingInvestments,
        dependents,
      });

      const { riskLevel, confidenceScore } = mlResponse.data;

      // Update assessment with ML results
      assessment.riskLevel = riskLevel;
      assessment.confidenceScore = confidenceScore;

      // Save assessment
      await this.riskAssessmentRepository.save(assessment);

      // Update user's risk profile
      const user = await this.userRepository.findOne({ where: { id: userId } });
      if (user) {
        user.riskProfile = riskLevel;
        await this.userRepository.save(user);
      }

      return res.json({
        message: 'Risk assessment completed successfully',
        assessment: {
          riskLevel,
          confidenceScore,
          recommendations: mlResponse.data.recommendations,
        },
      });
    } catch (error) {
      console.error('Risk assessment error:', error);
      return res.status(500).json({ message: 'Internal server error' });
    }
  };

  getAssessmentHistory = async (req: Request, res: Response): Promise<Response> => {
    try {
      const userId = req.user.id;

      const assessments = await this.riskAssessmentRepository.find({
        where: { userId },
        order: { createdAt: 'DESC' },
      });

      return res.json(assessments);
    } catch (error) {
      console.error('Assessment history fetch error:', error);
      return res.status(500).json({ message: 'Internal server error' });
    }
  };

  getPortfolioRecommendations = async (req: Request, res: Response): Promise<Response> => {
    try {
      const userId = req.user.id;

      // Get user's current risk profile
      const user = await this.userRepository.findOne({ where: { id: userId } });
      if (!user || !user.riskProfile) {
        return res.status(400).json({ message: 'Risk assessment required' });
      }

      // Get portfolio recommendations from ML service
      const mlResponse = await axios.get(
        `${this.ML_SERVICE_URL}/portfolio/recommendations`,
        {
          params: { riskLevel: user.riskProfile }
        }
      );

      return res.json({
        riskLevel: user.riskProfile,
        recommendations: mlResponse.data.recommendations,
        allocationStrategy: mlResponse.data.allocationStrategy,
      });
    } catch (error) {
      console.error('Portfolio recommendations error:', error);
      return res.status(500).json({ message: 'Internal server error' });
    }
  };

  updateRiskPreferences = async (req: Request, res: Response): Promise<Response> => {
    try {
      const userId = req.user.id;
      const { riskTolerance, investmentDuration } = req.body;

      // Get latest assessment
      const latestAssessment = await this.riskAssessmentRepository.findOne({
        where: { userId },
        order: { createdAt: 'DESC' },
      });

      if (!latestAssessment) {
        return res.status(404).json({ message: 'No previous assessment found' });
      }

      // Update assessment with new preferences
      latestAssessment.riskTolerance = riskTolerance;
      latestAssessment.investmentDuration = investmentDuration;

      // Recalculate risk level with ML service
      const mlResponse = await axios.post(`${this.ML_SERVICE_URL}/risk/analyze`, {
        ...latestAssessment,
        riskTolerance,
        investmentDuration,
      });

      const { riskLevel, confidenceScore } = mlResponse.data;

      // Update assessment and user
      latestAssessment.riskLevel = riskLevel;
      latestAssessment.confidenceScore = confidenceScore;
      await this.riskAssessmentRepository.save(latestAssessment);

      const user = await this.userRepository.findOne({ where: { id: userId } });
      if (user) {
        user.riskProfile = riskLevel;
        await this.userRepository.save(user);
      }

      return res.json({
        message: 'Risk preferences updated successfully',
        assessment: {
          riskLevel,
          confidenceScore,
          recommendations: mlResponse.data.recommendations,
        },
      });
    } catch (error) {
      console.error('Risk preferences update error:', error);
      return res.status(500).json({ message: 'Internal server error' });
    }
  };
}
