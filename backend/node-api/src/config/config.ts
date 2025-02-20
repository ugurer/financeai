import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const config = {
  port: process.env.NODE_API_PORT || 3001,
  jwtSecret: process.env.JWT_SECRET || 'your_jwt_secret_here',
  database: {
    url: process.env.DATABASE_URL || 'postgresql://user:password@localhost:5432/financeai',
  },
  cors: {
    origin: process.env.FRONTEND_URL || 'http://localhost:5173',
    credentials: true,
  },
};

export default config;
