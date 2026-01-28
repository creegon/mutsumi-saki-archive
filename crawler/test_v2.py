"""快速测试 Lofter 爬虫"""
import asyncio
from lofter_crawler_v2 import LofterCrawler

async def test():
    print("=" * 50)
    print("测试 Lofter 用户爬取")
    print("=" * 50)
    
    crawler = LofterCrawler(headless=True)
    await crawler.start()
    
    try:
        # 测试爬取一个用户的第一页
        posts = await crawler.get_user_posts('yurisa123', max_pages=1)
        
        print(f"\n找到 {len(posts)} 个帖子")
        for i, post in enumerate(posts[:3]):
            print(f"\n--- 帖子 {i+1} ---")
            print(f"标题: {post['title'][:50]}")
            print(f"作者: {post['author']}")
            print(f"图片数: {len(post['images'])}")
            print(f"URL: {post['url']}")
    finally:
        await crawler.close()

if __name__ == '__main__':
    asyncio.run(test())
