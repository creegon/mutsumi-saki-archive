import { Controller, Get, Post, Put, Delete, Body, Param, Query, UseGuards } from '@nestjs/common';
import { CrawlerService } from './crawler.service';
import { JwtAuthGuard } from '../auth';

@Controller('crawler')
@UseGuards(JwtAuthGuard)
export class CrawlerController {
  constructor(private crawlerService: CrawlerService) {}

  @Get()
  async findAll() {
    return this.crawlerService.findAll();
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    return this.crawlerService.findOne(id);
  }

  @Post()
  async create(@Body() body: {
    name: string;
    source: string;
    keywords: string[];
    schedule?: string;
  }) {
    return this.crawlerService.create(body);
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() body: any) {
    return this.crawlerService.update(id, body);
  }

  @Delete(':id')
  async delete(@Param('id') id: string) {
    return this.crawlerService.delete(id);
  }

  @Post(':id/start')
  async start(@Param('id') id: string) {
    return this.crawlerService.start(id);
  }

  @Post(':id/pause')
  async pause(@Param('id') id: string) {
    return this.crawlerService.pause(id);
  }

  @Post(':id/stop')
  async stop(@Param('id') id: string) {
    return this.crawlerService.stop(id);
  }

  @Get(':id/logs')
  async getLogs(@Param('id') id: string, @Query('limit') limit?: string) {
    return this.crawlerService.getLogs(id, limit ? parseInt(limit) : 100);
  }

  @Delete(':id/logs')
  async clearLogs(@Param('id') id: string) {
    return this.crawlerService.clearLogs(id);
  }
}
