"""
Lofter 爬虫 - 交互式版本
需要手动登录
"""
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from playwright.async_api import async_playwright

DATE_DELTA = timedelta(days=40732)

def parse_post_date(url):
    try:
        hex_time = url.split('_')[-1]
        timestamp = int(hex_time, 16)
        date = datetime.fromtimestamp(timestamp) - DATE_DELTA
        return date.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')

def get_original_url(url):
    if '?' in url:
        base = url.split('?')[0]
        return f"{base}?imageView&thumbnail=0x0&quality=100"
    return url

async def main():
    print("=" * 50)
    print("  Lofter 爬虫 - 交互式")
    print("=" * 50)
    
    async with async_playwright() as p:
        # 启动可见浏览器
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1400, 'height': 900})
        page = await context.new_page()
        
        # 1. 先去登录
        print("\n[1] 请在浏览器中登录 Lofter...")
        await page.goto('https://www.lofter.com/front/login')
        
        input("\n>>> 登录完成后按 Enter 继续...")
        
        # 2. 访问 Tag 页面
        tag = input("\n>>> 输入要爬取的 Tag (如 睦祥): ").strip() or "睦祥"
        url = f'https://www.lofter.com/tag/{quote(tag)}'
        
        print(f"\n[2] 访问: {url}")
        await page.goto(url, wait_until='networkidle')
        await asyncio.sleep(2)
        
        # 3. 滚动加载
        max_scroll = int(input(">>> 滚动次数 (默认 5): ").strip() or "5")
        
        print(f"\n[3] 开始滚动加载...")
        for i in range(max_scroll):
            print(f"    滚动 {i+1}/{max_scroll}")
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
        
        # 4. 收集帖子链接
        print("\n[4] 收集帖子链接...")
        links = await page.evaluate('''() => {
            const links = new Set();
            document.querySelectorAll('a').forEach(a => {
                if (a.href && a.href.match(/lofter\\.com\\/post\\/[0-9a-f]+_[0-9a-f]+/)) {
                    links.add(a.href);
                }
            });
            return Array.from(links);
        }''')
        
        print(f"    找到 {len(links)} 个帖子")
        
        if not links:
            print("[!] 没有找到帖子，可能需要登录或页面结构变化")
            await browser.close()
            return
        
        # 5. 获取每个帖子详情
        print("\n[5] 获取帖子详情...")
        posts = []
        
        for i, link in enumerate(links):
            print(f"    [{i+1}/{len(links)}] {link[:60]}...")
            
            try:
                post_page = await context.new_page()
                await post_page.goto(link, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(1)
                
                info = await post_page.evaluate('''() => {
                    let title = document.title || '';
                    
                    let author = '';
                    const authorEl = document.querySelector('[class*="author"], [class*="name"], .m-about a');
                    if (authorEl) author = authorEl.textContent.trim();
                    if (!author) {
                        const match = window.location.href.match(/https:\\/\\/([a-z0-9-]+)\\.lofter\\.com/);
                        if (match) author = match[1];
                    }
                    
                    const images = new Set();
                    document.querySelectorAll('[bigimgsrc]').forEach(el => images.add(el.getAttribute('bigimgsrc')));
                    document.querySelectorAll('[data-origin]').forEach(el => images.add(el.getAttribute('data-origin')));
                    document.querySelectorAll('img[src*="imglf"], img[src*="126.net"]').forEach(img => {
                        if (!img.src.includes('avatar')) images.add(img.src);
                    });
                    
                    const tags = [];
                    document.querySelectorAll('[class*="tag"], a[href*="/tag/"]').forEach(el => {
                        const t = el.textContent.trim().replace('#', '');
                        if (t && t.length < 30) tags.push(t);
                    });
                    
                    return { title, author, images: Array.from(images).filter(Boolean), tags: [...new Set(tags)] };
                }''')
                
                await post_page.close()
                
                if info and info['images']:
                    posts.append({
                        'title': info['title'],
                        'author': info['author'],
                        'url': link,
                        'date': parse_post_date(link),
                        'images': [get_original_url(img) for img in info['images']],
                        'tags': info['tags']
                    })
                    print(f"        ✓ {len(info['images'])} 张图")
                else:
                    print(f"        - 无图片")
                    
            except Exception as e:
                print(f"        ✗ 失败: {e}")
        
        await browser.close()
        
        # 6. 保存结果
        print(f"\n[6] 共获取 {len(posts)} 个有图帖子")
        
        if posts:
            output = Path('output')
            output.mkdir(exist_ok=True)
            filename = f'lofter_{tag}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            
            with open(output / filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            
            print(f"    保存到: {output / filename}")
            
            # 统计
            total_images = sum(len(p['images']) for p in posts)
            print(f"    帖子: {len(posts)}, 图片: {total_images}")
        
        print("\n完成!")

if __name__ == '__main__':
    asyncio.run(main())
