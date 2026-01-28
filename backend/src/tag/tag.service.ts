import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma';

@Injectable()
export class TagService {
  constructor(private prisma: PrismaService) {}

  async findAll(category?: string) {
    const where = category ? { category } : {};
    return this.prisma.tag.findMany({
      where,
      include: {
        _count: {
          select: { contents: true },
        },
      },
      orderBy: { name: 'asc' },
    });
  }

  async findPopular(limit = 20) {
    const tags = await this.prisma.tag.findMany({
      include: {
        _count: {
          select: { contents: true },
        },
      },
    });

    return tags
      .sort((a, b) => b._count.contents - a._count.contents)
      .slice(0, limit);
  }

  async create(name: string, category?: string) {
    return this.prisma.tag.create({
      data: { name, category },
    });
  }

  async update(id: string, data: { name?: string; category?: string }) {
    return this.prisma.tag.update({
      where: { id },
      data,
    });
  }

  async delete(id: string) {
    await this.prisma.tag.delete({ where: { id } });
    return { success: true };
  }
}
