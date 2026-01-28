"""
每日自动爬取任务
用于 Windows Task Scheduler 或手动运行
"""
import os
import sys
import logging
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'crawl_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_daily_crawl():
    """运行每日爬取"""
    from spiders.pixiv_spider import PixivSpider
    
    logger.info("=" * 60)
    logger.info("每日爬取任务开始")
    logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # 运行 Pixiv 爬虫
        # 每日爬取使用较小的页数，只抓取最新内容
        pixiv = PixivSpider()
        pixiv.run(max_pages=2, include_novels=True)
        
        logger.info("每日爬取任务完成")
        return True
        
    except Exception as e:
        logger.error(f"爬取任务出错: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    success = run_daily_crawl()
    sys.exit(0 if success else 1)
