"""
Lofter 爬虫 - 简化版
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
    print("  Lofter 爬虫")
    print("=" * 50)
    
    p = await async_playwright().start()
    
    try:
        # 启动浏览器 - 不要自动关闭
        print("\n[*] 启动浏览器...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1400, 'height': 900})
        page = await context.new_page()
        
        # 1. 登录
        print("[*] 打开登录页面...")
        await page.goto('https://www.lofter.com/front/login', timeout=60000)
        
        print("\n" + "=" * 50)
        print("请在浏览器中登录 Lofter！")
        print("登录完成后，回到这里按 Enter")
        print("=" * 50)
        
        # 等待用户输入
        await asyncio.get_event_loop().run_in_executor(None, input, "\n按 Enter 继续...")
        
        # 2. 爬取 Tag
        tag = await asyncio.get_event_loop().run_in_executor(None, input, "\n输入 Tag (默认 睦祥): ")
        tag = tag.strip() or "睦祥"
        
        url = f'https://www.lofter.com/tag/{quote(tag)}'
        print(f"\n[*] 访问: {url}")
        await page.goto(url, timeout=60000)
        await asyncio.sleep(3)
        
        # 3. 滚动
        scroll_times = await asyncio.get_event_loop().run_in_executor(None, input, "滚动次数 (默认 5): ")
        scroll_times = int(scroll_times.strip() or "5")
        
        print(f"\n[*] 滚动加载中...")
        for i in range(scroll_times):
            print(f"    滚动 {i+1}/{scroll_times}")
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
        
        # 4. 收集链接
        print("\n[*] 收集帖子链接...")
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
            print("[!] 没有找到帖子")
            return
        
        # 5. 获取详情
        print("\n[*] 获取帖子详情...")
        posts = []
        
        for i, link in enumerate(links[:50]):  # 最多50个
            print(f"    [{i+1}/{min(len(links), 50)}] {link[:50]}...")
            
            try:
                post_page = await context.new_page()
                await post_page.goto(link, timeout=30000)
                await asyncio.sleep(1)
                
                info = await post_page.evaluate('''() => {
                    let title = document.title || '';
                    let author = '';
                    
                    const match = window.location.href.match(/https:\\/\\/([a-z0-9-]+)\\.lofter\\.com/);
                    if (match) author = match[1];
                    
                    const images = new Set();
                    document.querySelectorAll('[bigimgsrc]').forEach(el => images.add(el.getAttribute('bigimgsrc')));
                    document.querySelectorAll('img[src*="imglf"], img[src*="126.net"]').forEach(img => {
                        if (!img.src.includes('avatar') && !img.src.includes('logo')) images.add(img.src);
                    });
                    
                    const tags = [];
                    document.querySelectorAll('a[href*="/tag/"]').forEach(el => {
                        const t = el.textContent.trim().replace('#', '');
                        if (t && t.length < 30 && !tags.includes(t)) tags.push(t);
                    });
                    
                    return { title, author, images: Array.from(images).filter(Boolean), tags };
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
                    print(f"        -> {len(info['images'])} 张图")
                    
            except Exception as e:
                print(f"        失败: {str(e)[:30]}")
        
        # 6. 保存
        if posts:
            output = Path('output')
            output.mkdir(exist_ok=True)
            filename = f'lofter_{tag}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            
            with open(output / filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            
            total_images = sum(len(p['images']) for p in posts)
            print(f"\n[*] 完成！")
            print(f"    帖子: {len(posts)}")
            print(f"    图片: {total_images}")
            print(f"    文件: output/{filename}")
        
    except Exception as e:
        print(f"\n[!] 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n按 Enter 关闭浏览器...")
        await asyncio.get_event_loop().run_in_executor(None, input)
        await p.stop()

if __name__ == '__main__':
    asyncio.run(main())
