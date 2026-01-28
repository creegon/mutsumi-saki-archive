import { CrawlerService } from './crawler.service';
export declare class CrawlerController {
    private crawlerService;
    constructor(crawlerService: CrawlerService);
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
    create(body: {
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
    update(id: string, body: any): Promise<{
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
    getLogs(id: string, limit?: string): Promise<{
        id: string;
        createdAt: Date;
        taskId: string;
        message: string;
        level: string;
    }[]>;
    clearLogs(id: string): Promise<{
        success: boolean;
    }>;
}
