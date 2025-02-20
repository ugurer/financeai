import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne, JoinColumn } from 'typeorm';
import { Portfolio } from './Portfolio';

@Entity('portfolio_holdings')
export class PortfolioHolding {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column()
    portfolio_id!: number;

    @Column()
    symbol!: string;

    @Column('decimal', { precision: 15, scale: 6 })
    quantity!: number;

    @Column('decimal', { precision: 15, scale: 2 })
    average_price!: number;

    @CreateDateColumn()
    last_updated!: Date;

    @ManyToOne(() => Portfolio)
    @JoinColumn({ name: 'portfolio_id' })
    portfolio!: Portfolio;
} 