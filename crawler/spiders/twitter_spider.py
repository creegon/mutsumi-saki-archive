"""
Twitter/X 爬虫 - 使用浏览器控制提取搜索结果
需要用户预先登录 Twitter
"""

import json
import re
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional


class TwitterSpider:
    def __init__(self, backend_url: str = "http://localhost:3001"):
        self.backend_url = backend_url
        self.browser_url = "http://127.0.0.1:18792"  # Clawdbot browser relay
        
    def search_tweets(self, query: str, max_scrolls: int = 5) -> List[Dict]:
        """
        通过浏览器搜索推文并提取结果
        这个方法会从 snapshot 中解析推文信息
        """
        results = []
        
        # 从浏览器快照中解析推文
        # 实际实现需要通过 Clawdbot 的 browser 工具来操作
        
        print(f"[Twitter] 搜索关键词: {query}")
        print(f"[Twitter] 需要通过 Clawdbot 浏览器控制来爬取")
        
        return results
    
    def extract_tweet_from_article(self, article_text: str) -> Optional[Dict]:
        """
        从 article 元素文本中提取推文信息
        """
        # 解析用户名
        username_match = re.search(r'@(\w+)', article_text)
        if not username_match:
            return None
            
        username = username_match.group(1)
        
        # 解析时间
        time_patterns = [
            r'(\d+h)',  # 4h
            r'(\d+m)',  # 30m
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+',  # Jan 14
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+,\s+\d{4}',  # Jan 14, 2025
        ]
        
        # 解析图片 URL（从 /photo/1 等链接）
        photo_matches = re.findall(r'/status/(\d+)/photo/\d+', article_text)
        
        # 解析互动数据
        likes_match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?K?)\s*(?:Likes?|like)', article_text, re.I)
        retweets_match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?K?)\s*reposts?', article_text, re.I)
        
        return {
            'username': username,
            'tweet_id': photo_matches[0] if photo_matches else None,
            'has_image': len(photo_matches) > 0,
            'likes': likes_match.group(1) if likes_match else '0',
            'retweets': retweets_match.group(1) if retweets_match else '0',
        }
    
    def submit_to_backend(self, data: Dict) -> bool:
        """提交数据到后端"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/content",
                json=data,
                timeout=30
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"[Twitter] 提交失败: {e}")
            return False


def parse_twitter_snapshot(snapshot_text: str) -> List[Dict]:
    """
    解析 Twitter 搜索结果快照，提取推文信息
    """
    tweets = []
    
    # 匹配 article 元素
    article_pattern = r'article "([^"]+)"'
    articles = re.findall(article_pattern, snapshot_text)
    
    for article in articles:
        # 提取用户名
        username_match = re.search(r'@(\w+)', article)
        if not username_match:
            continue
        
        # 提取推文 ID（从 URL）
        tweet_id_match = re.search(r'/status/(\d+)', article)
        
        # 检查是否有图片
        has_image = 'Image' in article or 'photo' in article
        
        # 提取互动数据
        likes_match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?K?)\s*(?:likes?|Likes)', article)
        retweets_match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?K?)\s*reposts?', article)
        
        if tweet_id_match and has_image:
            tweets.append({
                'username': username_match.group(1),
                'tweet_id': tweet_id_match.group(1),
                'has_image': True,
                'likes': likes_match.group(1) if likes_match else '0',
                'retweets': retweets_match.group(1) if retweets_match else '0',
                'tweet_url': f"https://x.com/{username_match.group(1)}/status/{tweet_id_match.group(1)}"
            })
    
    return tweets


if __name__ == "__main__":
    # 测试解析
    spider = TwitterSpider()
    print("Twitter Spider initialized")
    print("Use Clawdbot browser control to crawl Twitter")
