"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CrawlerService = void 0;
const common_1 = require("@nestjs/common");
const prisma_1 = require("../prisma");
let CrawlerService = class CrawlerService {
    prisma;
    constructor(prisma) {
        this.prisma = prisma;
    }
    async findAll() {
        const tasks = await this.prisma.crawlerTask.findMany({
            include: {
                logs: {
                    take: 10,
                    orderBy: { createdAt: 'desc' },
                },
            },
            orderBy: { createdAt: 'desc' },
        });
        return tasks.map(task => ({
            ...task,
            keywords: JSON.parse(task.keywords),
        }));
    }
    async findOne(id) {
        const task = await this.prisma.crawlerTask.findUnique({
            where: { id },
            include: {
                logs: {
                    orderBy: { createdAt: 'desc' },
                    take: 100,
                },
            },
        });
        if (!task)
            return null;
        return {
            ...task,
            keywords: JSON.parse(task.keywords),
        };
    }
    async create(data) {
        const task = await this.prisma.crawlerTask.create({
            data: {
                name: data.name,
                source: data.source,
                keywords: JSON.stringify(data.keywords),
                schedule: data.schedule,
                status: 'IDLE',
            },
        });
        return {
            ...task,
            keywords: JSON.parse(task.keywords),
        };
    }
    async update(id, data) {
        const updateData = {};
        if (data.name)
            updateData.name = data.name;
        if (data.keywords)
            updateData.keywords = JSON.stringify(data.keywords);
        if (data.schedule !== undefined)
            updateData.schedule = data.schedule;
        if (data.status)
            updateData.status = data.status;
        const task = await this.prisma.crawlerTask.update({
            where: { id },
            data: updateData,
        });
        return {
            ...task,
            keywords: JSON.parse(task.keywords),
        };
    }
    async delete(id) {
        await this.prisma.crawlerTask.delete({ where: { id } });
        return { success: true };
    }
    async start(id) {
        const task = await this.prisma.crawlerTask.update({
            where: { id },
            data: {
                status: 'RUNNING',
                lastRunAt: new Date(),
            },
        });
        return { ...task, keywords: JSON.parse(task.keywords) };
    }
    async pause(id) {
        const task = await this.prisma.crawlerTask.update({
            where: { id },
            data: { status: 'PAUSED' },
        });
        return { ...task, keywords: JSON.parse(task.keywords) };
    }
    async stop(id) {
        const task = await this.prisma.crawlerTask.update({
            where: { id },
            data: { status: 'IDLE' },
        });
        return { ...task, keywords: JSON.parse(task.keywords) };
    }
    async addLog(taskId, message, level = 'info') {
        return this.prisma.crawlerLog.create({
            data: {
                taskId,
                message,
                level,
            },
        });
    }
    async getLogs(taskId, limit = 100) {
        return this.prisma.crawlerLog.findMany({
            where: { taskId },
            orderBy: { createdAt: 'desc' },
            take: limit,
        });
    }
    async clearLogs(taskId) {
        await this.prisma.crawlerLog.deleteMany({ where: { taskId } });
        return { success: true };
    }
};
exports.CrawlerService = CrawlerService;
exports.CrawlerService = CrawlerService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [prisma_1.PrismaService])
], CrawlerService);
//# sourceMappingURL=crawler.service.js.map