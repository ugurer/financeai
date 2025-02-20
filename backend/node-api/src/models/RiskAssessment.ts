import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne, JoinColumn } from 'typeorm';
import { User } from './User';

@Entity('risk_assessments')
export class RiskAssessment {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column()
    user_id!: number;

    @Column()
    risk_level!: 'low' | 'medium' | 'high';

    @Column()
    investment_duration!: number;

    @Column()
    risk_tolerance!: number;

    @Column('text', { nullable: true })
    financial_goals?: string;

    @CreateDateColumn()
    created_at!: Date;

    @ManyToOne(() => User)
    @JoinColumn({ name: 'user_id' })
    user!: User;
} 