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
exports.TagService = void 0;
const common_1 = require("@nestjs/common");
const prisma_1 = require("../prisma");
let TagService = class TagService {
    prisma;
    constructor(prisma) {
        this.prisma = prisma;
    }
    async findAll(category) {
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
    async create(name, category) {
        return this.prisma.tag.create({
            data: { name, category },
        });
    }
    async update(id, data) {
        return this.prisma.tag.update({
            where: { id },
            data,
        });
    }
    async delete(id) {
        await this.prisma.tag.delete({ where: { id } });
        return { success: true };
    }
};
exports.TagService = TagService;
exports.TagService = TagService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [prisma_1.PrismaService])
], TagService);
//# sourceMappingURL=tag.service.js.map