import { Controller, Get, Res, Query } from '@nestjs/common';
import type { Response } from 'express';
import * as https from 'https';
import * as http from 'http';

@Controller('proxy')
export class ProxyController {
  @Get('image')
  async proxyImage(@Query('url') url: string, @Res() res: Response) {
    if (!url) {
      return res.status(400).send('Missing url parameter');
    }

    try {
      // Only allow pixiv images
      const allowedHosts = ['i.pximg.net', 'i-cf.pximg.net', 's.pximg.net'];
      const parsedUrl = new URL(url);
      
      if (!allowedHosts.some(host => parsedUrl.hostname.includes(host))) {
        return res.status(403).send('Host not allowed');
      }

      const protocol = parsedUrl.protocol === 'https:' ? https : http;
      
      const proxyReq = protocol.get(url, {
        headers: {
          'Referer': 'https://www.pixiv.net/',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
      }, (proxyRes) => {
        // Forward content type
        if (proxyRes.headers['content-type']) {
          res.setHeader('Content-Type', proxyRes.headers['content-type']);
        }
        if (proxyRes.headers['content-length']) {
          res.setHeader('Content-Length', proxyRes.headers['content-length']);
        }
        
        // Cache for 1 day
        res.setHeader('Cache-Control', 'public, max-age=86400');
        
        proxyRes.pipe(res);
      });

      proxyReq.on('error', (err) => {
        console.error('Proxy error:', err);
        res.status(500).send('Proxy error');
      });

    } catch (err) {
      console.error('Proxy error:', err);
      res.status(500).send('Proxy error');
    }
  }

  @Get('download')
  async downloadImage(
    @Query('url') url: string, 
    @Query('filename') filename: string,
    @Res() res: Response
  ) {
    if (!url) {
      return res.status(400).send('Missing url parameter');
    }

    try {
      // Only allow pixiv images
      const allowedHosts = ['i.pximg.net', 'i-cf.pximg.net', 's.pximg.net'];
      const parsedUrl = new URL(url);
      
      if (!allowedHosts.some(host => parsedUrl.hostname.includes(host))) {
        return res.status(403).send('Host not allowed');
      }

      const protocol = parsedUrl.protocol === 'https:' ? https : http;
      
      // Extract filename from URL if not provided
      const downloadFilename = filename || url.split('/').pop() || 'image.jpg';
      
      const proxyReq = protocol.get(url, {
        headers: {
          'Referer': 'https://www.pixiv.net/',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
      }, (proxyRes) => {
        // Set content type
        if (proxyRes.headers['content-type']) {
          res.setHeader('Content-Type', proxyRes.headers['content-type']);
        }
        if (proxyRes.headers['content-length']) {
          res.setHeader('Content-Length', proxyRes.headers['content-length']);
        }
        
        // Force download
        res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(downloadFilename)}"`);
        
        proxyRes.pipe(res);
      });

      proxyReq.on('error', (err) => {
        console.error('Download proxy error:', err);
        res.status(500).send('Download error');
      });

    } catch (err) {
      console.error('Download proxy error:', err);
      res.status(500).send('Download error');
    }
  }
}
