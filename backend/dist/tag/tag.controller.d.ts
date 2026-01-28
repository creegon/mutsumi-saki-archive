import { TagService } from './tag.service';
export declare class TagController {
    private tagService;
    constructor(tagService: TagService);
    findAll(category?: string): Promise<({
        _count: {
            contents: number;
        };
    } & {
        id: string;
        name: string;
        category: string | null;
    })[]>;
    findPopular(limit?: string): Promise<({
        _count: {
            contents: number;
        };
    } & {
        id: string;
        name: string;
        category: string | null;
    })[]>;
    create(body: {
        name: string;
        category?: string;
    }): Promise<{
        id: string;
        name: string;
        category: string | null;
    }>;
    update(id: string, body: {
        name?: string;
        category?: string;
    }): Promise<{
        id: string;
        name: string;
        category: string | null;
    }>;
    delete(id: string): Promise<{
        success: boolean;
    }>;
}
