"""
Main crawler runner
统一运行所有爬虫
"""
import argparse
import time
from spiders.pixiv_spider import PixivSpider
from spiders.lofter_spider import LofterSpider


def run_all(max_pages: int = 3):
    """运行所有爬虫"""
    print("=" * 50)
    print("睦祥资源站爬虫 - 开始运行")
    print("=" * 50)
    
    # Pixiv
    try:
        print("\n[1/2] 运行 Pixiv 爬虫...")
        pixiv = PixivSpider()
        pixiv.run(max_pages)
    except Exception as e:
        print(f"Pixiv 爬虫出错: {e}")
    
    time.sleep(2)
    
    # Lofter
    try:
        print("\n[2/2] 运行 Lofter 爬虫...")
        lofter = LofterSpider()
        lofter.run(max_pages)
    except Exception as e:
        print(f"Lofter 爬虫出错: {e}")
    
    print("\n" + "=" * 50)
    print("所有爬虫运行完成")
    print("=" * 50)


def run_single(spider_name: str, max_pages: int = 3):
    """运行单个爬虫"""
    spiders = {
        'pixiv': PixivSpider,
        'lofter': LofterSpider,
    }
    
    if spider_name.lower() not in spiders:
        print(f"未知爬虫: {spider_name}")
        print(f"可用爬虫: {', '.join(spiders.keys())}")
        return
    
    spider_class = spiders[spider_name.lower()]
    spider = spider_class()
    spider.run(max_pages)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='睦祥资源站爬虫')
    parser.add_argument('--spider', '-s', type=str, help='指定爬虫 (pixiv/lofter)')
    parser.add_argument('--pages', '-p', type=int, default=3, help='最大爬取页数')
    
    args = parser.parse_args()
    
    if args.spider:
        run_single(args.spider, args.pages)
    else:
        run_all(args.pages)
