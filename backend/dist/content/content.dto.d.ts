export declare class CreateContentDto {
    type: string;
    source: string;
    sourceUrl: string;
    sourceId?: string;
    title?: string;
    authorName?: string;
    authorId?: string;
    images?: string[];
    textContent?: string;
    tags?: string[];
    likes?: number;
    favorites?: number;
    publishedAt?: string;
}
export declare class UpdateContentDto {
    title?: string;
    textContent?: string;
    images?: string[];
    tags?: string[];
    likes?: number;
    favorites?: number;
}
export declare class QueryContentDto {
    type?: string;
    source?: string;
    search?: string;
    tag?: string;
    page?: number;
    limit?: number;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
}
