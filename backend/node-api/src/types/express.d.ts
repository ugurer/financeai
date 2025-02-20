import { Request } from 'express';

declare namespace Express {
    interface Request {
        user?: {
            userId: number;
            email?: string;
        }
    }
}

export {}; 