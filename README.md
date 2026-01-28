# 睦祥资源站 - 部署指南

## 快速启动（本地开发）

1. 启动后端：
```powershell
cd D:\mutsumi-saki-archive\backend
npm run start:dev
```

2. 启动前端：
```powershell
cd D:\mutsumi-saki-archive\frontend
npm run dev
```

3. 访问：
- 前端: http://localhost:3000
- 后端 API: http://localhost:3001/api
- 后台管理: http://localhost:3000/admin

## 管理员账号

- 用户名: `admin`
- 密码: `MutsumiSaki2024!`

## Pixiv 爬虫设置

### 1. 获取 Pixiv Refresh Token

首次使用需要获取 Pixiv OAuth Token：

```powershell
cd D:\mutsumi-saki-archive\crawler
pip install -r requirements.txt
python get_pixiv_token.py
```

按照提示操作：
1. 浏览器会打开 Pixiv 登录页面
2. 登录你的 Pixiv 账号
3. 登录后从 URL 复制 `code` 参数
4. 输入 code，脚本会自动更新 `.env` 文件

### 2. 手动运行爬虫

```powershell
cd D:\mutsumi-saki-archive\crawler
python main.py                    # 运行所有爬虫
python main.py -s pixiv           # 只运行 Pixiv
python main.py -s pixiv -p 5      # 爬取5页
```

### 3. 设置每日自动爬取

运行以下脚本创建 Windows 定时任务（每天凌晨3点自动爬取）：

```powershell
cd D:\mutsumi-saki-archive\crawler
.\setup_daily_task.ps1
```

或手动创建任务计划程序任务。

## 爬虫功能

### 支持的内容类型
- **插画** (IMAGE) - Pixiv 插画作品
- **漫画** (MANGA) - Pixiv 漫画作品
- **小说** (TEXT) - Pixiv 同人小说（包含完整正文）

### 搜索关键词
默认关键词在 `crawler/.env` 中配置：
```
KEYWORDS=若叶睦,丰川祥子,睦祥,祥睦,MutsumixSaki,ガルクラ
```

### 增量爬取
爬虫会自动跳过已存在的内容，只爬取新作品。

## 前端功能

### 图片查看器
- 点击图片打开全屏查看器
- 支持多图浏览（左右箭头或缩略图切换）
- 键盘快捷键：ESC 关闭，← → 切换

### 下载功能
- 悬停图片显示操作按钮
- 单张下载：查看器中点击下载按钮
- 批量下载：卡片悬停时点击下载图标

### 筛选和搜索
- 按类型筛选：插画/小说/漫画
- 按来源筛选：Pixiv/Lofter
- 搜索：标题、作者、标签
- 随机推荐

## 公网部署（使用 Cloudflare Tunnel）

### 方法 1: 使用 cloudflared（推荐）

1. 安装 cloudflared:
```powershell
winget install Cloudflare.cloudflared
```

2. 登录 Cloudflare:
```powershell
cloudflared tunnel login
```

3. 创建隧道:
```powershell
cloudflared tunnel create mutsumi-saki
```

4. 启动隧道（同时暴露前端和后端）:
```powershell
# 前端
cloudflared tunnel --url http://localhost:3000

# 后端 API（另一个终端）
cloudflared tunnel --url http://localhost:3001
```

Cloudflare 会给你一个临时公网地址，如 `https://xxx-xxx-xxx.trycloudflare.com`

### 方法 2: 使用 ngrok

1. 安装 ngrok: https://ngrok.com/download

2. 启动隧道:
```powershell
ngrok http 3000
```

### 方法 3: 使用 localtunnel

```powershell
npx localtunnel --port 3000
```

## 生产部署（完整版）

### 1. 构建前端
```powershell
cd D:\mutsumi-saki-archive\frontend
npm run build
```

### 2. 构建后端
```powershell
cd D:\mutsumi-saki-archive\backend
npm run build
```

### 3. 启动生产服务
```powershell
# 后端
cd D:\mutsumi-saki-archive\backend
npm run start:prod

# 前端
cd D:\mutsumi-saki-archive\frontend
npm run start
```

## 项目结构

```
D:\mutsumi-saki-archive\
├── backend/              # NestJS 后端
│   ├── prisma/           # 数据库 schema 和 SQLite 文件
│   └── src/              # 源代码
├── frontend/             # Next.js 前端
│   └── src/
│       ├── app/          # 页面
│       └── components/   # 组件（含 Lightbox 图片查看器）
├── crawler/              # Python 爬虫
│   ├── spiders/          # Pixiv, Lofter 爬虫
│   ├── get_pixiv_token.py    # OAuth Token 获取工具
│   ├── daily_crawl.py        # 每日爬取脚本
│   └── setup_daily_task.ps1  # Windows 定时任务设置
└── README.md
```

## API 端点

### 内容
- `GET /api/content` - 列表（支持分页、筛选、搜索）
- `GET /api/content/random` - 随机推荐
- `GET /api/content/stats` - 统计信息
- `GET /api/content/:id` - 详情
- `POST /api/content` - 创建（爬虫使用）
- `POST /api/content/:id/like` - 点赞
- `POST /api/content/:id/favorite` - 收藏

### 代理
- `GET /api/proxy/image?url=` - 代理 Pixiv 图片
- `GET /api/proxy/download?url=&filename=` - 下载 Pixiv 图片

### 认证
- `POST /api/auth/login` - 管理员登录
