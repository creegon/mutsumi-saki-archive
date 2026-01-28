"""
Lofter 爬虫 V3 - 需要登录
睦祥资源站专用

使用方法：
1. 第一次运行时会打开浏览器让你登录
2. 登录后会保存 Cookie，下次自动登录
3. 支持按用户/按Tag爬取
"""

import asyncio
import json
import os
import re
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote

from playwright.async_api import async_playwright, Page, Browser, BrowserContext

import requests

# ============ 配置 ============
COOKIE_FILE = Path(__file__).parent / 'lofter_cookies.pkl'
TIMEOUT = 60000  # ms
REQUEST_DELAY = 1.5  # seconds
DATE_DELTA = timedelta(days=40732)

# API 配置
API_URL = os.environ.get('API_URL', 'http://localhost:3001/api')
API_TOKEN = os.environ.get('API_TOKEN', '')

# ============ 工具函数 ============

def parse_post_date(url: str) -> str:
    try:
        hex_time = url.split('_')[-1]
        timestamp = int(hex_time, 16)
        date = datetime.fromtimestamp(timestamp) - DATE_DELTA
        return date.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')

def get_original_image_url(url: str) -> str:
    if '?' in url:
        base = url.split('?')[0]
        return f"{base}?imageView&thumbnail=0x0&quality=100&stripmeta=0"
    return url

# ============ 爬虫类 ============

class LofterCrawler:
    def __init__(self):
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.playwright = None
    
    async def start(self, headless: bool = False):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # 尝试加载已保存的 Cookie
        if COOKIE_FILE.exists():
            print('[*] 正在加载已保存的登录状态...')
            try:
                with open(COOKIE_FILE, 'rb') as f:
                    storage_state = pickle.load(f)
                self.context = await self.browser.new_context(
                    storage_state=storage_state,
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
                )
            except Exception as e:
                print(f'[!] 加载 Cookie 失败: {e}')
                self.context = await self._create_new_context()
        else:
            self.context = await self._create_new_context()
        
        self.page = await self.context.new_page()
    
    async def _create_new_context(self) -> BrowserContext:
        return await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        )
    
    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def save_cookies(self):
        """保存当前的登录状态"""
        storage = await self.context.storage_state()
        with open(COOKIE_FILE, 'wb') as f:
            pickle.dump(storage, f)
        print('[*] 登录状态已保存')
    
    async def ensure_logged_in(self) -> bool:
        """确保已登录，如果没有则引导用户登录"""
        print('[*] 检查登录状态...')
        
        # 访问首页检查登录
        await self.page.goto('https://www.lofter.com/', timeout=TIMEOUT)
        await asyncio.sleep(2)
        
        # 检查是否有登录按钮/登录表单
        login_indicator = await self.page.query_selector('text="登录"')
        
        if login_indicator:
            print('\n' + '=' * 50)
            print('[!] 需要登录 Lofter')
            print('[!] 请在打开的浏览器窗口中登录')
            print('[!] 登录完成后按 Enter 继续...')
            print('=' * 50 + '\n')
            
            # 跳转到登录页
            await self.page.goto('https://www.lofter.com/front/login', timeout=TIMEOUT)
            
            # 等待用户登录
            input()
            
            # 保存 Cookie
            await self.save_cookies()
            print('[*] 登录成功！')
            return True
        else:
            print('[*] 已登录')
            return True
    
    async def get_post_links_from_user(self, domain: str, max_pages: int = 0) -> List[str]:
        """获取用户所有帖子链接"""
        print(f'[*] 获取用户帖子链接: {domain}')
        
        all_links = set()
        page_num = 1
        
        while True:
            url = f'https://{domain}.lofter.com/' if page_num == 1 else f'https://{domain}.lofter.com/?page={page_num}'
            print(f'[*] 第 {page_num} 页: {url}')
            
            try:
                await self.page.goto(url, timeout=TIMEOUT, wait_until='networkidle')
                await asyncio.sleep(REQUEST_DELAY)
            except Exception as e:
                print(f'[!] 访问失败: {e}')
                break
            
            # 检查是否被重定向到登录页
            current_url = self.page.url
            if 'login' in current_url.lower():
                print('[!] 被重定向到登录页，需要重新登录')
                await self.ensure_logged_in()
                continue
            
            # 获取帖子链接
            links = await self.page.evaluate('''(domain) => {
                const links = new Set();
                const pattern = new RegExp(`https://${domain}\\.lofter\\.com/post/[0-9a-f]+_[0-9a-f]+`);
                document.querySelectorAll('a').forEach(a => {
                    if (a.href && pattern.test(a.href)) {
                        links.add(a.href);
                    }
                });
                return Array.from(links);
            }''', domain)
            
            if not links:
                print(f'[*] 第 {page_num} 页没有帖子，结束')
                break
            
            new_count = len([l for l in links if l not in all_links])
            all_links.update(links)
            print(f'    找到 {new_count} 个新帖子 (总计 {len(all_links)})')
            
            page_num += 1
            if max_pages and page_num > max_pages:
                break
        
        return list(all_links)
    
    async def get_post_links_from_tag(self, tag: str, max_scroll: int = 10) -> List[str]:
        """获取 Tag 下的帖子链接"""
        print(f'[*] 获取 Tag 帖子链接: {tag}')
        
        url = f'https://www.lofter.com/tag/{quote(tag)}'
        print(f'[*] 访问: {url}')
        
        try:
            await self.page.goto(url, timeout=TIMEOUT, wait_until='networkidle')
            await asyncio.sleep(REQUEST_DELAY)
        except Exception as e:
            print(f'[!] 访问失败: {e}')
            return []
        
        # 检查登录
        if 'login' in self.page.url.lower():
            print('[!] 需要登录才能访问 Tag 页面')
            await self.ensure_logged_in()
            return await self.get_post_links_from_tag(tag, max_scroll)
        
        all_links = set()
        
        for i in range(max_scroll):
            print(f'[*] 滚动加载 {i + 1}/{max_scroll}...')
            
            # 获取当前链接
            links = await self.page.evaluate('''() => {
                const links = new Set();
                document.querySelectorAll('a').forEach(a => {
                    if (a.href && a.href.match(/lofter\\.com\\/post\\/[0-9a-f]+_[0-9a-f]+/)) {
                        links.add(a.href);
                    }
                });
                return Array.from(links);
            }''')
            
            new_count = len([l for l in links if l not in all_links])
            all_links.update(links)
            print(f'    找到 {new_count} 个新帖子 (总计 {len(all_links)})')
            
            if new_count == 0:
                # 尝试滚动
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(2)
                
                # 再检查一次
                links2 = await self.page.evaluate('''() => {
                    const links = new Set();
                    document.querySelectorAll('a').forEach(a => {
                        if (a.href && a.href.match(/lofter\\.com\\/post\\/[0-9a-f]+_[0-9a-f]+/)) {
                            links.add(a.href);
                        }
                    });
                    return Array.from(links);
                }''')
                
                if len([l for l in links2 if l not in all_links]) == 0:
                    print('[*] 没有更多内容了')
                    break
            
            # 滚动加载更多
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(REQUEST_DELAY)
        
        return list(all_links)
    
    async def get_post_info(self, url: str) -> Optional[Dict]:
        """获取帖子详情"""
        try:
            page = await self.context.new_page()
            await page.goto(url, timeout=TIMEOUT, wait_until='networkidle')
            await asyncio.sleep(1)
            
            info = await page.evaluate('''() => {
                // 标题
                let title = document.title || '';
                
                // 作者
                let author = '';
                const authorEl = document.querySelector('.personcardname, .author-name, .m-about a, [class*="author"]');
                if (authorEl) author = authorEl.textContent.trim();
                
                // 从 URL 提取作者
                if (!author) {
                    const match = window.location.href.match(/https:\\/\\/([a-zA-Z0-9-]+)\\.lofter\\.com/);
                    if (match) author = match[1];
                }
                
                // 图片 - 多种方式获取
                const images = new Set();
                
                // 方式1: bigimgsrc 属性
                document.querySelectorAll('[bigimgsrc]').forEach(el => {
                    images.add(el.getAttribute('bigimgsrc'));
                });
                
                // 方式2: data-origin 属性
                document.querySelectorAll('[data-origin]').forEach(el => {
                    images.add(el.getAttribute('data-origin'));
                });
                
                // 方式3: img 标签 src
                document.querySelectorAll('img[src*="imglf"], img[src*="126.net"]').forEach(img => {
                    let src = img.src;
                    // 过滤掉头像等小图
                    if (!src.includes('avatar') && !src.includes('icon')) {
                        images.add(src);
                    }
                });
                
                // 方式4: 背景图
                document.querySelectorAll('[style*="background-image"]').forEach(el => {
                    const style = el.getAttribute('style');
                    const match = style.match(/url\\(["\']?(https?:\\/\\/[^"\'\\)]+)["\']?\\)/);
                    if (match && (match[1].includes('imglf') || match[1].includes('126.net'))) {
                        images.add(match[1]);
                    }
                });
                
                // 正文
                let text = '';
                const textEl = document.querySelector('.content .text, .m-post .text, .post-content, article');
                if (textEl) text = textEl.textContent.trim();
                
                // 标签
                const tags = new Set();
                document.querySelectorAll('.tag, a[href*="/tag/"]').forEach(el => {
                    let t = el.textContent.trim().replace('#', '');
                    if (t) tags.add(t);
                });
                
                return {
                    title,
                    author,
                    images: Array.from(images).filter(Boolean),
                    text,
                    tags: Array.from(tags)
                };
            }''')
            
            await page.close()
            
            if not info or not info['images']:
                return None
            
            return {
                'title': info['title'],
                'author': info['author'],
                'url': url,
                'date': parse_post_date(url),
                'text': info['text'],
                'images': [get_original_image_url(img) for img in info['images']],
                'tags': info['tags'],
            }
        
        except Exception as e:
            print(f'[!] 获取帖子失败: {url} - {e}')
            return None

# ============ 保存功能 ============

def save_to_api(posts: List[Dict]):
    if not API_TOKEN:
        print('[!] 未设置 API_TOKEN，请设置环境变量')
        return
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }
    
    saved, skipped, failed = 0, 0, 0
    
    for post in posts:
        data = {
            'type': 'IMAGE',
            'source': 'LOFTER',
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
                print(f'[+] {post["title"][:40]}')
            elif r.status_code == 409:
                skipped += 1
            else:
                failed += 1
                print(f'[!] 失败: {r.status_code}')
        except Exception as e:
            failed += 1
            print(f'[!] 错误: {e}')
    
    print(f'\n[*] 保存: {saved}, 跳过: {skipped}, 失败: {failed}')

def save_to_local(posts: List[Dict], output_dir: str = 'output'):
    output = Path(output_dir)
    output.mkdir(exist_ok=True)
    
    filename = f'lofter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output / filename, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    
    print(f'[*] 保存到 {output / filename}')
    print(f'[*] 共 {len(posts)} 个帖子, {sum(len(p["images"]) for p in posts)} 张图片')

# ============ 主程序 ============

async def main():
    print('=' * 50)
    print('  Lofter 爬虫 V3')
    print('  睦祥资源站专用')
    print('=' * 50)
    print()
    print('1. 按用户爬取')
    print('2. 按 Tag 爬取')
    print()
    
    mode = input('选择模式 (1/2): ').strip()
    
    crawler = LofterCrawler()
    # 第一次运行时显示浏览器让用户登录
    await crawler.start(headless=COOKIE_FILE.exists())
    
    posts = []
    
    try:
        await crawler.ensure_logged_in()
        
        if mode == '1':
            domain = input('用户域名: ').strip()
            max_pages = input('最大页数 (0=全部): ').strip()
            max_pages = int(max_pages) if max_pages else 0
            
            links = await crawler.get_post_links_from_user(domain, max_pages)
            print(f'\n[*] 获取帖子详情 ({len(links)} 个)...')
            
            for i, link in enumerate(links):
                print(f'[{i+1}/{len(links)}] {link}')
                info = await crawler.get_post_info(link)
                if info and info['images']:
                    posts.append(info)
                    print(f'    -> {len(info["images"])} 张图')
        
        elif mode == '2':
            tag = input('Tag: ').strip()
            max_scroll = input('最大滚动次数 (默认10): ').strip()
            max_scroll = int(max_scroll) if max_scroll else 10
            
            links = await crawler.get_post_links_from_tag(tag, max_scroll)
            print(f'\n[*] 获取帖子详情 ({len(links)} 个)...')
            
            for i, link in enumerate(links):
                print(f'[{i+1}/{len(links)}] {link}')
                info = await crawler.get_post_info(link)
                if info and info['images']:
                    posts.append(info)
                    print(f'    -> {len(info["images"])} 张图')
    
    finally:
        await crawler.close()
    
    if not posts:
        print('[!] 没有找到任何帖子')
        return
    
    print(f'\n[*] 共 {len(posts)} 个帖子')
    print('\n1. 保存到 API')
    print('2. 保存到本地')
    print('3. 两者都保存')
    
    save = input('保存方式 (1/2/3): ').strip()
    
    if save in ['1', '3']:
        save_to_api(posts)
    if save in ['2', '3']:
        save_to_local(posts)
    
    print('\n[*] 完成!')

if __name__ == '__main__':
    asyncio.run(main())
