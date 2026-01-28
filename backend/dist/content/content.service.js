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
exports.ContentService = void 0;
const common_1 = require("@nestjs/common");
const prisma_1 = require("../prisma");
let ContentService = class ContentService {
    prisma;
    constructor(prisma) {
        this.prisma = prisma;
    }
    async create(dto) {
        const { tags, images, ...data } = dto;
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
            const uniqueTags = [...new Set(tags)];
            for (const tagName of uniqueTags) {
                let tag = await this.prisma.tag.findUnique({ where: { name: tagName } });
                if (!tag) {
                    tag = await this.prisma.tag.create({ data: { name: tagName } });
                }
                await this.prisma.contentTag.upsert({
                    where: { contentId_tagId: { contentId: content.id, tagId: tag.id } },
                    create: { contentId: content.id, tagId: tag.id },
                    update: {},
                });
            }
        }
        return this.findOne(content.id);
    }
    async findAll(query) {
        const page = query.page || 1;
        const limit = query.limit || 20;
        const skip = (page - 1) * limit;
        const where = {};
        if (query.type)
            where.type = query.type;
        if (query.source)
            where.source = query.source;
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
        const orderBy = {};
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
    async findOne(id) {
        const content = await this.prisma.content.findUnique({
            where: { id },
            include: {
                tags: {
                    include: { tag: true },
                },
            },
        });
        if (!content)
            return null;
        return {
            ...content,
            images: JSON.parse(content.images),
            tags: content.tags.map(t => t.tag.name),
        };
    }
    async findRandom(limit = 10, type) {
        const where = {};
        if (type)
            where.type = type;
        const count = await this.prisma.content.count({ where });
        if (count === 0)
            return [];
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
    async update(id, dto) {
        const { tags, images, ...data } = dto;
        const updateData = { ...data };
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
    async delete(id) {
        await this.prisma.content.delete({ where: { id } });
        return { success: true };
    }
    async like(id) {
        const content = await this.prisma.content.update({
            where: { id },
            data: { likes: { increment: 1 } },
        });
        return { ...content, images: JSON.parse(content.images) };
    }
    async favorite(id) {
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
            }, {}),
            bySource: bySource.reduce((acc, item) => {
                acc[item.source] = item._count;
                return acc;
            }, {}),
        };
    }
};
exports.ContentService = ContentService;
exports.ContentService = ContentService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [prisma_1.PrismaService])
], ContentService);
//# sourceMappingURL=content.service.js.map