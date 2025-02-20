import express, { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { User } from '../models/User';
import { AppDataSource } from '../app';

const router = express.Router();
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

// Kayıt olma
router.post('/register', async (req: Request, res: Response) => {
    try {
        console.log('Register request body:', req.body);
        
        const userRepository = AppDataSource.getRepository(User);
        const { email, password, firstName, lastName } = req.body;

        if (!email || !password) {
            return res.status(400).json({ error: 'Email ve şifre zorunludur.' });
        }

        // E-posta kontrolü
        const existingUser = await userRepository.findOne({ where: { email } });
        if (existingUser) {
            return res.status(400).json({ error: 'Bu e-posta adresi zaten kayıtlı.' });
        }

        // Şifre hash'leme
        const hashedPassword = await bcrypt.hash(password, 10);

        // Yeni kullanıcı oluşturma
        const user = new User();
        user.email = email;
        user.password_hash = hashedPassword;
        user.first_name = firstName || null;
        user.last_name = lastName || null;

        console.log('Creating user:', user);

        const savedUser = await userRepository.save(user);
        console.log('User saved:', savedUser);

        // JWT token oluştur
        const token = jwt.sign({ userId: savedUser.id }, JWT_SECRET, { expiresIn: '24h' });

        return res.status(201).json({
            message: 'Kullanıcı başarıyla oluşturuldu.',
            token,
            user: {
                id: savedUser.id,
                email: savedUser.email,
                firstName: savedUser.first_name,
                lastName: savedUser.last_name
            }
        });
    } catch (error) {
        console.error('Kayıt hatası:', error);
        return res.status(500).json({ error: 'Kayıt işlemi sırasında bir hata oluştu.' });
    }
});

// Giriş yapma
router.post('/login', async (req: Request, res: Response) => {
    try {
        const userRepository = AppDataSource.getRepository(User);
        const { email, password } = req.body;

        // Kullanıcı kontrolü
        const user = await userRepository.findOne({ where: { email } });
        if (!user) {
            return res.status(401).json({ error: 'Geçersiz e-posta veya şifre.' });
        }

        // Şifre kontrolü
        const isValidPassword = await bcrypt.compare(password, user.password_hash);
        if (!isValidPassword) {
            return res.status(401).json({ error: 'Geçersiz e-posta veya şifre.' });
        }

        // JWT token oluştur
        const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: '24h' });

        return res.json({
            message: 'Giriş başarılı.',
            token,
            user: {
                id: user.id,
                email: user.email,
                firstName: user.first_name,
                lastName: user.last_name
            }
        });
    } catch (error) {
        console.error('Giriş hatası:', error);
        return res.status(500).json({ error: 'Giriş işlemi sırasında bir hata oluştu.' });
    }
});

export default router;