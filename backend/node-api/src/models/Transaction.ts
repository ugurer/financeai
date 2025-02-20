import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne, JoinColumn } from 'typeorm';
import { Portfolio } from './Portfolio';

@Entity('transactions')
export class Transaction {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column()
    portfolio_id!: number;

    @Column()
    symbol!: string;

    @Column()
    transaction_type!: 'buy' | 'sell';

    @Column('decimal', { precision: 10, scale: 2 })
    quantity!: number;

    @Column('decimal', { precision: 10, scale: 2 })
    price!: number;

    @Column('decimal', { precision: 10, scale: 2 })
    total_amount!: number;

    @CreateDateColumn()
    transaction_date!: Date;

    @ManyToOne(() => Portfolio)
    @JoinColumn({ name: 'portfolio_id' })
    portfolio!: Portfolio;
} 