import { Request, Response } from 'express';
import { getRepository } from 'typeorm';
import { User } from '../entities/User';
import { compare, hash } from 'bcrypt';
import { sign } from 'jsonwebtoken';
import { validateEmail, validatePassword } from '../utils/validators';

export class AuthController {
  private userRepository = getRepository(User);
  private JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

  register = async (req: Request, res: Response): Promise<Response> => {
    try {
      const { email, password, firstName, lastName } = req.body;

      // Validate input
      if (!validateEmail(email)) {
        return res.status(400).json({ message: 'Invalid email format' });
      }

      if (!validatePassword(password)) {
        return res.status(400).json({ 
          message: 'Password must be at least 8 characters long and contain at least one number and one special character' 
        });
      }

      // Check if user already exists
      const existingUser = await this.userRepository.findOne({ where: { email } });
      if (existingUser) {
        return res.status(400).json({ message: 'User already exists' });
      }

      // Hash password
      const hashedPassword = await hash(password, 10);

      // Create new user
      const user = this.userRepository.create({
        email,
        passwordHash: hashedPassword,
        firstName,
        lastName,
      });

      await this.userRepository.save(user);

      // Generate JWT token
      const token = sign({ userId: user.id }, this.JWT_SECRET, { expiresIn: '24h' });

      return res.status(201).json({
        message: 'User registered successfully',
        token,
        user: {
          id: user.id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
        },
      });
    } catch (error) {
      console.error('Registration error:', error);
      return res.status(500).json({ message: 'Internal server error' });
    }
  };

  login = async (req: Request, res: Response): Promise<Response> => {
    try {
      const { email, password } = req.body;

      // Find user
      const user = await this.userRepository.findOne({ where: { email } });
      if (!user) {
        return res.status(401).json({ message: 'Invalid credentials' });
      }

      // Verify password
      const isPasswordValid = await compare(password, user.passwordHash);
      if (!isPasswordValid) {
        return res.status(401).json({ message: 'Invalid credentials' });
      }

      // Generate JWT token
      const token = sign({ userId: user.id }, this.JWT_SECRET, { expiresIn: '24h' });

      return res.json({
        message: 'Login successful',
        token,
        user: {
          id: user.id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
        },
      });
    } catch (error) {
      console.error('Login error:', error);
      return res.status(500).json({ message: 'Internal server error' });
    }
  };

  verifyToken = async (req: Request, res: Response): Promise<Response> => {
    try {
      // User data is attached to request by auth middleware
      const user = req.user;
      
      return res.json({
        message: 'Token is valid',
        user: {
          id: user.id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
        },
      });
    } catch (error) {
      console.error('Token verification error:', error);
      return res.status(500).json({ message: 'Internal server error' });
    }
  };
}
