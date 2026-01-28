import { Controller, Get, Post, Put, Delete, Body, Param, Query, UseGuards } from '@nestjs/common';
import { TagService } from './tag.service';
import { JwtAuthGuard } from '../auth';

@Controller('tag')
export class TagController {
  constructor(private tagService: TagService) {}

  @Get()
  async findAll(@Query('category') category?: string) {
    return this.tagService.findAll(category);
  }

  @Get('popular')
  async findPopular(@Query('limit') limit?: string) {
    return this.tagService.findPopular(limit ? parseInt(limit) : 20);
  }

  @UseGuards(JwtAuthGuard)
  @Post()
  async create(@Body() body: { name: string; category?: string }) {
    return this.tagService.create(body.name, body.category);
  }

  @UseGuards(JwtAuthGuard)
  @Put(':id')
  async update(@Param('id') id: string, @Body() body: { name?: string; category?: string }) {
    return this.tagService.update(id, body);
  }

  @UseGuards(JwtAuthGuard)
  @Delete(':id')
  async delete(@Param('id') id: string) {
    return this.tagService.delete(id);
  }
}
