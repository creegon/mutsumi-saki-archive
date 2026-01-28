"""快速测试 - 看看 Lofter 页面结构"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    print("=" * 50)
    print("探索 Lofter 页面结构")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 访问一个用户页面
        url = 'https://yurisa123.lofter.com/'
        print(f"访问: {url}")
        
        await page.goto(url, timeout=60000)
        await asyncio.sleep(3)  # 等待 JS 渲染
        
        # 获取页面内容
        content = await page.content()
        print(f"页面长度: {len(content)}")
        
        # 打印前 3000 字符看结构
        print("\n页面内容:")
        print(content[:3000])
        
        # 尝试找链接
        links = await page.evaluate('''() => {
            const allLinks = [];
            document.querySelectorAll('a').forEach(a => {
                if (a.href.includes('lofter.com')) {
                    allLinks.push(a.href);
                }
            });
            return allLinks;
        }''')
        
        print(f"\n找到 {len(links)} 个 lofter 链接:")
        for link in links[:10]:
            print(f"  {link}")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test())
