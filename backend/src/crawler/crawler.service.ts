import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma';

@Injectable()
export class CrawlerService {
  constructor(private prisma: PrismaService) {}

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

  async findOne(id: string) {
    const task = await this.prisma.crawlerTask.findUnique({
      where: { id },
      include: {
        logs: {
          orderBy: { createdAt: 'desc' },
          take: 100,
        },
      },
    });
    
    if (!task) return null;
    
    return {
      ...task,
      keywords: JSON.parse(task.keywords),
    };
  }

  async create(data: {
    name: string;
    source: string;
    keywords: string[];
    schedule?: string;
  }) {
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

  async update(id: string, data: {
    name?: string;
    keywords?: string[];
    schedule?: string;
    status?: string;
  }) {
    const updateData: any = {};
    if (data.name) updateData.name = data.name;
    if (data.keywords) updateData.keywords = JSON.stringify(data.keywords);
    if (data.schedule !== undefined) updateData.schedule = data.schedule;
    if (data.status) updateData.status = data.status;
    
    const task = await this.prisma.crawlerTask.update({
      where: { id },
      data: updateData,
    });
    
    return {
      ...task,
      keywords: JSON.parse(task.keywords),
    };
  }

  async delete(id: string) {
    await this.prisma.crawlerTask.delete({ where: { id } });
    return { success: true };
  }

  async start(id: string) {
    const task = await this.prisma.crawlerTask.update({
      where: { id },
      data: {
        status: 'RUNNING',
        lastRunAt: new Date(),
      },
    });
    return { ...task, keywords: JSON.parse(task.keywords) };
  }

  async pause(id: string) {
    const task = await this.prisma.crawlerTask.update({
      where: { id },
      data: { status: 'PAUSED' },
    });
    return { ...task, keywords: JSON.parse(task.keywords) };
  }

  async stop(id: string) {
    const task = await this.prisma.crawlerTask.update({
      where: { id },
      data: { status: 'IDLE' },
    });
    return { ...task, keywords: JSON.parse(task.keywords) };
  }

  async addLog(taskId: string, message: string, level = 'info') {
    return this.prisma.crawlerLog.create({
      data: {
        taskId,
        message,
        level,
      },
    });
  }

  async getLogs(taskId: string, limit = 100) {
    return this.prisma.crawlerLog.findMany({
      where: { taskId },
      orderBy: { createdAt: 'desc' },
      take: limit,
    });
  }

  async clearLogs(taskId: string) {
    await this.prisma.crawlerLog.deleteMany({ where: { taskId } });
    return { success: true };
  }
}
