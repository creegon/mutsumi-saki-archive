import type { Response } from 'express';
export declare class ProxyController {
    proxyImage(url: string, res: Response): Promise<Response<any, Record<string, any>> | undefined>;
    downloadImage(url: string, filename: string, res: Response): Promise<Response<any, Record<string, any>> | undefined>;
}
