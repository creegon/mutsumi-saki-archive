import { OnModuleInit } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { PrismaService } from '../prisma';
import { ConfigService } from '@nestjs/config';
export declare class AuthService implements OnModuleInit {
    private prisma;
    private jwtService;
    private configService;
    constructor(prisma: PrismaService, jwtService: JwtService, configService: ConfigService);
    onModuleInit(): Promise<void>;
    validateAdmin(username: string, password: string): Promise<{
        id: string;
        username: string;
        password: string;
        createdAt: Date;
        updatedAt: Date;
    }>;
    login(username: string, password: string): Promise<{
        access_token: string;
        admin: {
            id: string;
            username: string;
        };
    }>;
    validateToken(payload: any): Promise<{
        id: string;
        username: string;
        password: string;
        createdAt: Date;
        updatedAt: Date;
    } | null>;
}
