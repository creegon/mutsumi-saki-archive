import { PrismaService } from '../prisma';
export declare class CrawlerService {
    private prisma;
    constructor(prisma: PrismaService);
    findAll(): Promise<{
        keywords: any;
        logs: {
            id: string;
            createdAt: Date;
            taskId: string;
            message: string;
            level: string;
        }[];
        id: string;
        createdAt: Date;
        updatedAt: Date;
        name: string;
        source: string;
        status: string;
        schedule: string | null;
        lastRunAt: Date | null;
        nextRunAt: Date | null;
    }[]>;
    findOne(id: string): Promise<{
        keywords: any;
        logs: {
            id: string;
            createdAt: Date;
            taskId: string;
            message: string;
            level: string;
        }[];
        id: string;
        createdAt: Date;
        updatedAt: Date;
        name: string;
        source: string;
        status: string;
        schedule: string | null;
        lastRunAt: Date | null;
        nextRunAt: Date | null;
    } | null>;
    create(data: {
        name: string;
        source: string;
        keywords: string[];
        schedule?: string;
    }): Promise<{
        keywords: any;
        id: string;
        createdAt: Date;
        updatedAt: Date;
        name: string;
        source: string;
        status: string;
        schedule: string | null;
        lastRunAt: Date | null;
        nextRunAt: Date | null;
    }>;
    update(id: string, data: {
        name?: string;
        keywords?: string[];
        schedule?: string;
        status?: string;
    }): Promise<{
        keywords: any;
        id: string;
        createdAt: Date;
        updatedAt: Date;
        name: string;
        source: string;
        status: string;
        schedule: string | null;
        lastRunAt: Date | null;
        nextRunAt: Date | null;
    }>;
    delete(id: string): Promise<{
        success: boolean;
    }>;
    start(id: string): Promise<{
        keywords: any;
        id: string;
        createdAt: Date;
        updatedAt: Date;
        name: string;
        source: string;
        status: string;
        schedule: string | null;
        lastRunAt: Date | null;
        nextRunAt: Date | null;
    }>;
    pause(id: string): Promise<{
        keywords: any;
        id: string;
        createdAt: Date;
        updatedAt: Date;
        name: string;
        source: string;
        status: string;
        schedule: string | null;
        lastRunAt: Date | null;
        nextRunAt: Date | null;
    }>;
    stop(id: string): Promise<{
        keywords: any;
        id: string;
        createdAt: Date;
        updatedAt: Date;
        name: string;
        source: string;
        status: string;
        schedule: string | null;
        lastRunAt: Date | null;
        nextRunAt: Date | null;
    }>;
    addLog(taskId: string, message: string, level?: string): Promise<{
        id: string;
        createdAt: Date;
        taskId: string;
        message: string;
        level: string;
    }>;
    getLogs(taskId: string, limit?: number): Promise<{
        id: string;
        createdAt: Date;
        taskId: string;
        message: string;
        level: string;
    }[]>;
    clearLogs(taskId: string): Promise<{
        success: boolean;
    }>;
}
