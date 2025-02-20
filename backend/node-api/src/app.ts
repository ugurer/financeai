import 'reflect-metadata';
import express from 'express';
import cors from 'cors';
import { DataSource } from 'typeorm';
import dotenv from 'dotenv';
import authRoutes from './routes/auth';
import portfolioRoutes from './routes/portfolio';
import transactionRoutes from './routes/transaction';
import riskRoutes from './routes/risk';
import { User } from './models/User';
import { Portfolio } from './models/Portfolio';
import { PortfolioHolding } from './models/PortfolioHolding';
import { Transaction } from './models/Transaction';
import { RiskAssessment } from './models/RiskAssessment';

dotenv.config();

const app = express();

// CORS ayarları
app.use(cors({
    origin: ['http://localhost:3000', 'http://localhost:3001'],
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true
}));

app.use(express.json());

// Veritabanı bağlantısı
export const AppDataSource = new DataSource({
    type: "postgres",
    host: process.env.DB_HOST || "postgres",  // Docker Compose service name
    port: parseInt(process.env.DB_PORT || "5432"),
    username: process.env.DB_USER || "postgres",
    password: process.env.DB_PASSWORD || "postgres",
    database: process.env.DB_NAME || "finance_ai",
    entities: [User, Portfolio, PortfolioHolding, Transaction, RiskAssessment],
    synchronize: true,
    logging: true
});

// Veritabanı bağlantısını başlat ve sunucuyu çalıştır
AppDataSource.initialize()
    .then(() => {
        console.log("Veritabanı bağlantısı başarılı");
        
        // Routes
        app.use('/api/auth', authRoutes);
        app.use('/api/portfolio', portfolioRoutes);
        app.use('/api/transactions', transactionRoutes);
        app.use('/api/risk', riskRoutes);

        // Error handling middleware
        app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
            console.error(err.stack);
            res.status(500).json({ error: 'Bir hata oluştu!' });
        });

        // Sunucuyu başlat
        const PORT = process.env.PORT || 3001;
        app.listen(PORT, () => {
            console.log(`Sunucu ${PORT} portunda çalışıyor`);
        });
    })
    .catch((error) => {
        console.error("Veritabanı bağlantısı başarısız:", error);
        process.exit(1);
    });