import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { PrismaModule } from './prisma';
import { AuthModule } from './auth';
import { ContentModule } from './content';
import { TagModule } from './tag';
import { CrawlerModule } from './crawler';
import { ProxyModule } from './proxy/proxy.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    PrismaModule,
    AuthModule,
    ContentModule,
    TagModule,
    CrawlerModule,
    ProxyModule,
  ],
})
export class AppModule {}
