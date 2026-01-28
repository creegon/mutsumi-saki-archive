"""
Lofter 爬虫 V2 - 使用 Playwright 支持 JavaScript 渲染
睦祥资源站专用
"""

import asyncio
import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote, unquote

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    print("请先安装 playwright: pip install playwright")
    print("然后运行: playwright install chromium")
    exit(1)

import requests

# ============ 配置 ============
TIMEOUT = 60000  # 毫秒
REQUEST_DELAY = 2  # 秒
DATE_DELTA = timedelta(days=40732)

# API 配置
API_URL = os.environ.get('API_URL', 'http://localhost:3001/api')
API_TOKEN = os.environ.get('API_TOKEN', '')

# ============ 工具函数 ============

def parse_post_date(url: str) -> str:
    """从帖子 URL 解析日期"""
    try:
        hex_time = url.split('_')[-1]
        timestamp = int(hex_time, 16)
        date = datetime.fromtimestamp(timestamp) - DATE_DELTA
        return date.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')

def clean_filename(name: str) -> str:
    """清理文件名"""
    return re.sub(r'[\\/:*?"<>|]', '_', name)[:100]

def get_image_original_url(url: str) -> str:
    """获取原图 URL"""
    if '?' in url:
        base_url = url.split('?')[0]
        return f"{base_url}?imageView&thumbnail=0x0&quality=100&stripmeta=0"
    return url

# ============ Playwright 爬虫 ============

class LofterCrawler:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Browser = None
        self.page: Page = None
    
    async def start(self):
        """启动浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = await context.new_page()
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
    
    async def login_if_needed(self):
        """如果需要登录，提示用户手动登录"""
        await self.page.goto('https://www.lofter.com/', timeout=TIMEOUT)
        await asyncio.sleep(2)
        
        # 检查是否已登录
        content = await self.page.content()
        if '登录' in content or 'login' in content.lower():
            print("\n[!] 检测到需要登录")
            print("[!] 请在打开的浏览器窗口中手动登录 Lofter")
            print("[!] 登录完成后按 Enter 继续...")
            
            # 临时改为非 headless 模式让用户登录
            if self.headless:
                await self.close()
                self.headless = False
                await self.start()
                await self.page.goto('https://www.lofter.com/front/login', timeout=TIMEOUT)
            
            input()
            print("[*] 继续爬取...")
    
    async def get_user_posts(self, domain: str, max_pages: int = 0) -> List[Dict]:
        """
        爬取用户的所有帖子
        """
        print(f'[*] 开始爬取用户: {domain}')
        
        all_posts = []
        page_num = 1
        
        while True:
            url = f'https://{domain}.lofter.com/?page={page_num}' if page_num > 1 else f'https://{domain}.lofter.com/'
            print(f'[*] 正在获取第 {page_num} 页: {url}')
            
            try:
                await self.page.goto(url, timeout=TIMEOUT, wait_until='networkidle')
                await asyncio.sleep(REQUEST_DELAY)
                
                # 等待内容加载
                await self.page.wait_for_selector('.m-post, .post, .g-bd, article', timeout=10000)
            except Exception as e:
                print(f'[!] 页面加载失败: {e}')
                break
            
            # 获取帖子链接
            post_links = await self.page.evaluate('''() => {
                const links = new Set();
                document.querySelectorAll('a[href*="/post/"]').forEach(a => {
                    const href = a.href;
                    if (href.match(/lofter\\.com\\/post\\/[0-9a-f]+_[0-9a-f]+/)) {
                        links.add(href);
                    }
                });
                return Array.from(links);
            }''')
            
            if not post_links:
                print(f'[*] 第 {page_num} 页没有帖子，结束')
                break
            
            print(f'    找到 {len(post_links)} 个帖子')
            
            # 获取每个帖子的详情
            for link in post_links:
                post_info = await self.get_post_info(link)
                if post_info and post_info['images']:
                    all_posts.append(post_info)
            
            page_num += 1
            if max_pages and page_num > max_pages:
                break
        
        return all_posts
    
    async def get_tag_posts(self, tag: str, max_pages: int = 10) -> List[Dict]:
        """
        按 Tag 爬取帖子
        """
        print(f'[*] 开始爬取 Tag: {tag}')
        
        # 先确保登录
        await self.login_if_needed()
        
        all_posts = []
        seen_links = set()
        
        # 访问 tag 页面
        encoded_tag = quote(tag)
        url = f'https://www.lofter.com/tag/{encoded_tag}'
        
        print(f'[*] 访问: {url}')
        await self.page.goto(url, timeout=TIMEOUT, wait_until='networkidle')
        await asyncio.sleep(REQUEST_DELAY)
        
        for page_num in range(1, max_pages + 1):
            print(f'[*] 正在获取第 {page_num} 页...')
            
            # 滚动加载更多
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
            
            # 获取帖子链接
            post_links = await self.page.evaluate('''() => {
                const links = new Set();
                document.querySelectorAll('a[href*="/post/"]').forEach(a => {
                    const href = a.href;
                    if (href.match(/lofter\\.com\\/post\\/[0-9a-f]+_[0-9a-f]+/)) {
                        links.add(href);
                    }
                });
                return Array.from(links);
            }''')
            
            new_links = [l for l in post_links if l not in seen_links]
            print(f'    找到 {len(new_links)} 个新帖子')
            
            if not new_links:
                print('[*] 没有更多帖子了')
                break
            
            for link in new_links:
                seen_links.add(link)
                post_info = await self.get_post_info(link)
                if post_info and post_info['images']:
                    all_posts.append(post_info)
            
            # 点击加载更多（如果有）
            try:
                load_more = await self.page.query_selector('.load-more, .m-loadmore, button:has-text("加载更多")')
                if load_more:
                    await load_more.click()
                    await asyncio.sleep(2)
            except:
                pass
        
        return all_posts
    
    async def get_post_info(self, url: str) -> Optional[Dict]:
        """获取帖子详情"""
        try:
            # 新建标签页访问帖子
            page = await self.browser.new_page()
            await page.goto(url, timeout=TIMEOUT, wait_until='networkidle')
            await asyncio.sleep(1)
            
            # 提取信息
            info = await page.evaluate('''() => {
                // 标题
                let title = document.title || '';
                
                // 作者
                let author = '';
                const authorEl = document.querySelector('.personcardname, .author, .m-info a');
                if (authorEl) author = authorEl.textContent.trim();
                
                // 图片
                const images = [];
                document.querySelectorAll('[bigimgsrc], img[src*="imglf"], img[src*="126.net"]').forEach(img => {
                    let src = img.getAttribute('bigimgsrc') || img.src;
                    if (src && !images.includes(src)) {
                        images.push(src);
                    }
                });
                
                // 文字内容
                let text = '';
                const contentEl = document.querySelector('.content .text, .m-post .text, .post-content');
                if (contentEl) text = contentEl.textContent.trim();
                
                // 标签
                const tags = [];
                document.querySelectorAll('.tag, a[href*="/tag/"]').forEach(tag => {
                    const t = tag.textContent.trim().replace('#', '');
                    if (t && !tags.includes(t)) tags.push(t);
                });
                
                return { title, author, images, text, tags };
            }''')
            
            await page.close()
            
            if not info:
                return None
            
            # 处理图片 URL
            images = [get_image_original_url(img) for img in info['images']]
            
            return {
                'title': info['title'],
                'author': info['author'],
                'url': url,
                'date': parse_post_date(url),
                'text': info['text'],
                'images': images,
                'tags': info['tags'],
            }
        
        except Exception as e:
            print(f'[!] 获取帖子失败: {url} - {e}')
            return None

# ============ 保存功能 ============

def save_to_api(posts: List[Dict], source: str = 'LOFTER'):
    """保存到后端 API"""
    if not API_TOKEN:
        print('[!] 未设置 API_TOKEN')
        return
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }
    
    saved = 0
    for post in posts:
        if not post['images']:
            continue
        
        data = {
            'type': 'IMAGE',
            'source': source,
            'sourceUrl': post['url'],
            'title': post['title'],
            'authorName': post['author'],
            'images': post['images'],
            'textContent': post.get('text', ''),
            'tags': post.get('tags', []),
        }
        
        try:
            r = requests.post(f'{API_URL}/content', json=data, headers=headers, timeout=30)
            if r.status_code == 201:
                saved += 1
                print(f'[+] 保存成功: {post["title"][:30]}...')
            elif r.status_code == 409:
                print(f'[-] 已存在: {post["title"][:30]}...')
            else:
                print(f'[!] 保存失败 ({r.status_code}): {r.text[:100]}')
        except Exception as e:
            print(f'[!] API 错误: {e}')
    
    print(f'\n[*] 完成！保存 {saved} 个')

def save_to_local(posts: List[Dict], output_dir: str = 'output'):
    """保存到本地"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    json_file = output_path / f'lofter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    
    print(f'[*] 已保存到 {json_file}')

# ============ 主程序 ============

async def main():
    print('=' * 50)
    print('  Lofter 爬虫 V2 (Playwright)')
    print('  睦祥资源站专用')
    print('=' * 50)
    print()
    print('选择模式:')
    print('1. 按用户爬取')
    print('2. 按 Tag 爬取')
    print()
    
    mode = input('请选择 (1/2): ').strip()
    headless = input('无头模式? (y/n, 默认y): ').strip().lower() != 'n'
    
    crawler = LofterCrawler(headless=headless)
    await crawler.start()
    
    posts = []
    
    try:
        if mode == '1':
            domain = input('用户域名 (如 coldiron): ').strip()
            max_pages = input('最大页数 (0=全部): ').strip()
            max_pages = int(max_pages) if max_pages else 0
            posts = await crawler.get_user_posts(domain, max_pages)
        
        elif mode == '2':
            tag = input('Tag 名称 (如 睦祥): ').strip()
            max_pages = input('最大页数 (默认10): ').strip()
            max_pages = int(max_pages) if max_pages else 10
            posts = await crawler.get_tag_posts(tag, max_pages)
        
        else:
            print('[!] 无效选择')
            return
    
    finally:
        await crawler.close()
    
    if not posts:
        print('[!] 没有找到任何帖子')
        return
    
    print(f'\n[*] 共获取 {len(posts)} 个帖子')
    
    # 保存
    print('\n保存方式:')
    print('1. 保存到 API')
    print('2. 保存到本地')
    print('3. 两者')
    
    save_mode = input('请选择 (1/2/3): ').strip()
    
    if save_mode in ['1', '3']:
        save_to_api(posts)
    if save_mode in ['2', '3']:
        save_to_local(posts)
    
    print('\n[*] 完成!')

if __name__ == '__main__':
    asyncio.run(main())
