import { getRepository } from 'typeorm';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { User } from '../models/User';

export class AuthService {
    private static readonly JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
    private static readonly JWT_EXPIRES_IN = '24h';

    public static async register(email: string, password: string, firstName?: string, lastName?: string): Promise<User> {
        const userRepository = getRepository(User);

        // E-posta kontrolü
        const existingUser = await userRepository.findOne({ where: { email } });
        if (existingUser) {
            throw new Error('Bu e-posta adresi zaten kayıtlı.');
        }

        // Şifre hash'leme
        const hashedPassword = await bcrypt.hash(password, 10);

        // Yeni kullanıcı oluşturma
        const user = userRepository.create({
            email,
            password_hash: hashedPassword,
            first_name: firstName,
            last_name: lastName
        });

        await userRepository.save(user);
        return user;
    }

    public static async login(email: string, password: string): Promise<{ token: string; user: Partial<User> }> {
        const userRepository = getRepository(User);
        const user = await userRepository.findOne({ where: { email } });

        if (!user) {
            throw new Error('Geçersiz e-posta veya şifre.');
        }

        const validPassword = await bcrypt.compare(password, user.password_hash);
        if (!validPassword) {
            throw new Error('Geçersiz e-posta veya şifre.');
        }

        const token = jwt.sign(
            { userId: user.id },
            this.JWT_SECRET,
            { expiresIn: this.JWT_EXPIRES_IN }
        );

        // Hassas bilgileri çıkar
        const { password_hash, ...userWithoutPassword } = user;

        return {
            token,
            user: userWithoutPassword
        };
    }

    public static async validateToken(token: string): Promise<{ userId: number }> {
        try {
            const decoded = jwt.verify(token, this.JWT_SECRET) as { userId: number };
            return decoded;
        } catch (error) {
            throw new Error('Geçersiz token.');
        }
    }

    public static async getUserById(userId: number): Promise<Partial<User>> {
        const userRepository = getRepository(User);
        const user = await userRepository.findOne({ where: { id: userId } });

        if (!user) {
            throw new Error('Kullanıcı bulunamadı.');
        }

        // Hassas bilgileri çıkar
        const { password_hash, ...userWithoutPassword } = user;
        return userWithoutPassword;
    }
} 