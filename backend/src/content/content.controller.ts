import { Controller, Get, Post, Put, Delete, Body, Param, Query, UseGuards } from '@nestjs/common';
import { ContentService } from './content.service';
import { CreateContentDto, UpdateContentDto, QueryContentDto } from './content.dto';
import { JwtAuthGuard } from '../auth';

@Controller('content')
export class ContentController {
  constructor(private contentService: ContentService) {}

  @Get()
  async findAll(@Query() query: QueryContentDto) {
    return this.contentService.findAll(query);
  }

  @Get('random')
  async findRandom(@Query('limit') limit?: string, @Query('type') type?: string) {
    return this.contentService.findRandom(limit ? parseInt(limit) : 10, type);
  }

  @Get('stats')
  async getStats() {
    return this.contentService.getStats();
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    return this.contentService.findOne(id);
  }

  @Post()
  async create(@Body() dto: CreateContentDto) {
    return this.contentService.create(dto);
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() dto: UpdateContentDto) {
    return this.contentService.update(id, dto);
  }

  @UseGuards(JwtAuthGuard)
  @Delete(':id')
  async delete(@Param('id') id: string) {
    return this.contentService.delete(id);
  }

  @Post(':id/like')
  async like(@Param('id') id: string) {
    return this.contentService.like(id);
  }

  @Post(':id/favorite')
  async favorite(@Param('id') id: string) {
    return this.contentService.favorite(id);
  }
}
