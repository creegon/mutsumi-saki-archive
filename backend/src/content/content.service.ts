import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma';
import { CreateContentDto, UpdateContentDto, QueryContentDto } from './content.dto';

@Injectable()
export class ContentService {
  constructor(private prisma: PrismaService) {}

  async create(dto: CreateContentDto) {
    const { tags, images, ...data } = dto;
    
    // 检查是否已存在
    const existing = await this.prisma.content.findUnique({
      where: { sourceUrl: dto.sourceUrl },
    });
    if (existing) {
      return { ...existing, images: JSON.parse(existing.images), tags: [] };
    }
    
    const content = await this.prisma.content.create({
      data: {
        ...data,
        images: JSON.stringify(images || []),
        publishedAt: dto.publishedAt ? new Date(dto.publishedAt) : null,
      },
    });

    if (tags && tags.length > 0) {
      const uniqueTags = [...new Set(tags)]; // 去重
      for (const tagName of uniqueTags) {
        let tag = await this.prisma.tag.findUnique({ where: { name: tagName } });
        if (!tag) {
          tag = await this.prisma.tag.create({ data: { name: tagName } });
        }
        // 使用 upsert 避免重复
        await this.prisma.contentTag.upsert({
          where: { contentId_tagId: { contentId: content.id, tagId: tag.id } },
          create: { contentId: content.id, tagId: tag.id },
          update: {},
        });
      }
    }

    return this.findOne(content.id);
  }

  async findAll(query: QueryContentDto) {
    const page = query.page || 1;
    const limit = query.limit || 20;
    const skip = (page - 1) * limit;

    const where: any = {};
    
    if (query.type) where.type = query.type;
    if (query.source) where.source = query.source;
    if (query.search) {
      where.OR = [
        { title: { contains: query.search } },
        { authorName: { contains: query.search } },
      ];
    }
    if (query.tag) {
      where.tags = {
        some: {
          tag: { name: query.tag },
        },
      };
    }

    const orderBy: any = {};
    const sortBy = query.sortBy || 'createdAt';
    const sortOrder = query.sortOrder || 'desc';
    orderBy[sortBy] = sortOrder;

    const [items, total] = await Promise.all([
      this.prisma.content.findMany({
        where,
        include: {
          tags: {
            include: { tag: true },
          },
        },
        skip,
        take: limit,
        orderBy,
      }),
      this.prisma.content.count({ where }),
    ]);

    return {
      items: items.map(item => ({
        ...item,
        images: JSON.parse(item.images),
        tags: item.tags.map(t => t.tag.name),
      })),
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    };
  }

  async findOne(id: string) {
    const content = await this.prisma.content.findUnique({
      where: { id },
      include: {
        tags: {
          include: { tag: true },
        },
      },
    });

    if (!content) return null;

    return {
      ...content,
      images: JSON.parse(content.images),
      tags: content.tags.map(t => t.tag.name),
    };
  }

  async findRandom(limit = 10, type?: string) {
    const where: any = {};
    if (type) where.type = type;

    const count = await this.prisma.content.count({ where });
    if (count === 0) return [];

    const randomSkip = Math.max(0, Math.floor(Math.random() * count) - limit);
    
    const items = await this.prisma.content.findMany({
      where,
      include: {
        tags: {
          include: { tag: true },
        },
      },
      skip: randomSkip,
      take: limit,
    });

    return items.map(item => ({
      ...item,
      images: JSON.parse(item.images),
      tags: item.tags.map(t => t.tag.name),
    }));
  }

  async update(id: string, dto: UpdateContentDto) {
    const { tags, images, ...data } = dto;

    const updateData: any = { ...data };
    if (images) {
      updateData.images = JSON.stringify(images);
    }

    await this.prisma.content.update({
      where: { id },
      data: updateData,
    });

    if (tags !== undefined) {
      await this.prisma.contentTag.deleteMany({ where: { contentId: id } });
      
      for (const tagName of tags) {
        let tag = await this.prisma.tag.findUnique({ where: { name: tagName } });
        if (!tag) {
          tag = await this.prisma.tag.create({ data: { name: tagName } });
        }
        await this.prisma.contentTag.create({
          data: { contentId: id, tagId: tag.id },
        });
      }
    }

    return this.findOne(id);
  }

  async delete(id: string) {
    await this.prisma.content.delete({ where: { id } });
    return { success: true };
  }

  async like(id: string) {
    const content = await this.prisma.content.update({
      where: { id },
      data: { likes: { increment: 1 } },
    });
    return { ...content, images: JSON.parse(content.images) };
  }

  async favorite(id: string) {
    const content = await this.prisma.content.update({
      where: { id },
      data: { favorites: { increment: 1 } },
    });
    return { ...content, images: JSON.parse(content.images) };
  }

  async getStats() {
    const total = await this.prisma.content.count();
    
    const byType = await this.prisma.content.groupBy({
      by: ['type'],
      _count: true,
    });
    
    const bySource = await this.prisma.content.groupBy({
      by: ['source'],
      _count: true,
    });

    return {
      total,
      byType: byType.reduce((acc, item) => {
        acc[item.type] = item._count;
        return acc;
      }, {} as Record<string, number>),
      bySource: bySource.reduce((acc, item) => {
        acc[item.source] = item._count;
        return acc;
      }, {} as Record<string, number>),
    };
  }
}
