import { IsString, IsOptional, IsArray, IsIn, IsDateString, IsNumber } from 'class-validator';
import { Type } from 'class-transformer';

const CONTENT_TYPES = ['TEXT', 'IMAGE', 'MANGA'] as const;
const CONTENT_SOURCES = ['PIXIV', 'LOFTER', 'TWITTER', 'MANUAL'] as const;

export class CreateContentDto {
  @IsIn(CONTENT_TYPES)
  type: string;

  @IsIn(CONTENT_SOURCES)
  source: string;

  @IsString()
  sourceUrl: string;

  @IsOptional()
  @IsString()
  sourceId?: string;

  @IsOptional()
  @IsString()
  title?: string;

  @IsOptional()
  @IsString()
  authorName?: string;

  @IsOptional()
  @IsString()
  authorId?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  images?: string[];

  @IsOptional()
  @IsString()
  textContent?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  tags?: string[];

  @IsOptional()
  @IsNumber()
  likes?: number;

  @IsOptional()
  @IsNumber()
  favorites?: number;

  @IsOptional()
  @IsDateString()
  publishedAt?: string;
}

export class UpdateContentDto {
  @IsOptional()
  @IsString()
  title?: string;

  @IsOptional()
  @IsString()
  textContent?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  images?: string[];

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  tags?: string[];

  @IsOptional()
  @IsNumber()
  likes?: number;

  @IsOptional()
  @IsNumber()
  favorites?: number;
}

export class QueryContentDto {
  @IsOptional()
  @IsIn(CONTENT_TYPES)
  type?: string;

  @IsOptional()
  @IsIn(CONTENT_SOURCES)
  source?: string;

  @IsOptional()
  @IsString()
  search?: string;

  @IsOptional()
  @IsString()
  tag?: string;

  @IsOptional()
  @Type(() => Number)
  page?: number;

  @IsOptional()
  @Type(() => Number)
  limit?: number;

  @IsOptional()
  @IsString()
  sortBy?: string;

  @IsOptional()
  @IsString()
  sortOrder?: 'asc' | 'desc';
}
