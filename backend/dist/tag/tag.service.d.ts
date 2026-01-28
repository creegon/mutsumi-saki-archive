import { PrismaService } from '../prisma';
export declare class TagService {
    private prisma;
    constructor(prisma: PrismaService);
    findAll(category?: string): Promise<({
        _count: {
            contents: number;
        };
    } & {
        id: string;
        name: string;
        category: string | null;
    })[]>;
    findPopular(limit?: number): Promise<({
        _count: {
            contents: number;
        };
    } & {
        id: string;
        name: string;
        category: string | null;
    })[]>;
    create(name: string, category?: string): Promise<{
        id: string;
        name: string;
        category: string | null;
    }>;
    update(id: string, data: {
        name?: string;
        category?: string;
    }): Promise<{
        id: string;
        name: string;
        category: string | null;
    }>;
    delete(id: string): Promise<{
        success: boolean;
    }>;
}
