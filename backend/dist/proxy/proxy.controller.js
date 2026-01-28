"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProxyController = void 0;
const common_1 = require("@nestjs/common");
const https = __importStar(require("https"));
const http = __importStar(require("http"));
let ProxyController = class ProxyController {
    async proxyImage(url, res) {
        if (!url) {
            return res.status(400).send('Missing url parameter');
        }
        try {
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
                if (proxyRes.headers['content-type']) {
                    res.setHeader('Content-Type', proxyRes.headers['content-type']);
                }
                if (proxyRes.headers['content-length']) {
                    res.setHeader('Content-Length', proxyRes.headers['content-length']);
                }
                res.setHeader('Cache-Control', 'public, max-age=86400');
                proxyRes.pipe(res);
            });
            proxyReq.on('error', (err) => {
                console.error('Proxy error:', err);
                res.status(500).send('Proxy error');
            });
        }
        catch (err) {
            console.error('Proxy error:', err);
            res.status(500).send('Proxy error');
        }
    }
    async downloadImage(url, filename, res) {
        if (!url) {
            return res.status(400).send('Missing url parameter');
        }
        try {
            const allowedHosts = ['i.pximg.net', 'i-cf.pximg.net', 's.pximg.net'];
            const parsedUrl = new URL(url);
            if (!allowedHosts.some(host => parsedUrl.hostname.includes(host))) {
                return res.status(403).send('Host not allowed');
            }
            const protocol = parsedUrl.protocol === 'https:' ? https : http;
            const downloadFilename = filename || url.split('/').pop() || 'image.jpg';
            const proxyReq = protocol.get(url, {
                headers: {
                    'Referer': 'https://www.pixiv.net/',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                },
            }, (proxyRes) => {
                if (proxyRes.headers['content-type']) {
                    res.setHeader('Content-Type', proxyRes.headers['content-type']);
                }
                if (proxyRes.headers['content-length']) {
                    res.setHeader('Content-Length', proxyRes.headers['content-length']);
                }
                res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(downloadFilename)}"`);
                proxyRes.pipe(res);
            });
            proxyReq.on('error', (err) => {
                console.error('Download proxy error:', err);
                res.status(500).send('Download error');
            });
        }
        catch (err) {
            console.error('Download proxy error:', err);
            res.status(500).send('Download error');
        }
    }
};
exports.ProxyController = ProxyController;
__decorate([
    (0, common_1.Get)('image'),
    __param(0, (0, common_1.Query)('url')),
    __param(1, (0, common_1.Res)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, Object]),
    __metadata("design:returntype", Promise)
], ProxyController.prototype, "proxyImage", null);
__decorate([
    (0, common_1.Get)('download'),
    __param(0, (0, common_1.Query)('url')),
    __param(1, (0, common_1.Query)('filename')),
    __param(2, (0, common_1.Res)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, String, Object]),
    __metadata("design:returntype", Promise)
], ProxyController.prototype, "downloadImage", null);
exports.ProxyController = ProxyController = __decorate([
    (0, common_1.Controller)('proxy')
], ProxyController);
//# sourceMappingURL=proxy.controller.js.map