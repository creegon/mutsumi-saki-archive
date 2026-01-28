"""
Lofter Spider for MutsumiSaki Archive
爬取 Lofter 上的睦祥相关内容
"""
import os
import re
import time
from typing import Optional, List
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class LofterSpider:
    def __init__(self, backend_url: str = None):
        self.backend_url = backend_url or os.getenv('BACKEND_URL', 'http://localhost:3001/api')
        self.keywords = os.getenv('KEYWORDS', '睦祥,祥睦').split(',')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
    
    def search(self, keyword: str, max_pages: int = 5) -> List[dict]:
        """搜索 Lofter 标签页"""
        results = []
        
        # Lofter 标签页 URL
        tag_url = f'https://www.lofter.com/tag/{keyword}'
        
        try:
            print(f"[Lofter] 搜索标签: {keyword}")
            resp = self.session.get(tag_url, timeout=15)
            
            if resp.status_code != 200:
                print(f"[Lofter] 请求失败: {resp.status_code}")
                return results
            
            soup = BeautifulSoup(resp.text, 'lxml')
            
            # 找到文章列表
            posts = soup.select('.post, .m-post, article')
            
            for post in posts[:50]:  # 限制数量
                content = self._parse_post(post, keyword)
                if content:
                    results.append(content)
            
            print(f"[Lofter] 标签 '{keyword}' 找到 {len(results)} 个结果")
            
        except Exception as e:
            print(f"[Lofter] 搜索出错: {e}")
        
        return results
    
    def _parse_post(self, post_elem, keyword: str) -> Optional[dict]:
        """解析单个帖子"""
        try:
            # 尝试获取链接
            link_elem = post_elem.select_one('a[href*="lofter.com"]')
            if not link_elem:
                link_elem = post_elem.select_one('a.permalink, a.title, a')
            
            source_url = link_elem.get('href', '') if link_elem else ''
            if not source_url or 'lofter.com' not in source_url:
                return None
            
            # 获取标题
            title_elem = post_elem.select_one('.title, .tit, h2, h3')
            title = title_elem.get_text(strip=True) if title_elem else f'Lofter - {keyword}'
            
            # 获取作者
            author_elem = post_elem.select_one('.author, .name, .nick')
            author_name = author_elem.get_text(strip=True) if author_elem else '未知作者'
            
            # 获取图片
            images = []
            img_elems = post_elem.select('img[src*="imglf"], img[data-src]')
            for img in img_elems[:10]:
                src = img.get('src') or img.get('data-src')
                if src and 'imglf' in src:
                    images.append(src)
            
            # 获取文字内容
            content_elem = post_elem.select_one('.content, .text, .body, p')
            text_content = content_elem.get_text(strip=True)[:2000] if content_elem else ''
            
            # 判断类型
            content_type = 'IMAGE' if images else 'TEXT'
            
            return {
                'type': content_type,
                'source': 'LOFTER',
                'sourceUrl': source_url,
                'sourceId': self._extract_post_id(source_url),
                'title': title[:200],
                'authorName': author_name,
                'authorId': None,
                'images': images,
                'textContent': text_content,
                'tags': [keyword],
                'publishedAt': None,
            }
            
        except Exception as e:
            print(f"[Lofter] 解析帖子出错: {e}")
            return None
    
    def _extract_post_id(self, url: str) -> str:
        """从 URL 提取帖子 ID"""
        match = re.search(r'/post/([a-f0-9_]+)', url)
        if match:
            return match.group(1)
        return url
    
    def crawl_user_blog(self, blog_name: str, max_posts: int = 50) -> List[dict]:
        """爬取特定用户的博客"""
        results = []
        blog_url = f'https://{blog_name}.lofter.com'
        
        try:
            print(f"[Lofter] 爬取博客: {blog_name}")
            resp = self.session.get(blog_url, timeout=15)
            
            if resp.status_code != 200:
                print(f"[Lofter] 博客请求失败: {resp.status_code}")
                return results
            
            soup = BeautifulSoup(resp.text, 'lxml')
            posts = soup.select('.post, article, .m-post')
            
            for post in posts[:max_posts]:
                content = self._parse_post(post, blog_name)
                if content:
                    content['authorName'] = blog_name
                    results.append(content)
            
            print(f"[Lofter] 博客 '{blog_name}' 找到 {len(results)} 个帖子")
            
        except Exception as e:
            print(f"[Lofter] 爬取博客出错: {e}")
        
        return results
    
    def submit_to_backend(self, content: dict) -> bool:
        """提交内容到后端"""
        try:
            resp = requests.post(
                f'{self.backend_url}/content',
                json=content,
                timeout=10
            )
            if resp.status_code in [200, 201]:
                print(f"[Lofter] 提交成功: {content['title'][:30]}")
                return True
            elif resp.status_code == 409:
                print(f"[Lofter] 已存在: {content['title'][:30]}")
                return True
            else:
                print(f"[Lofter] 提交失败 ({resp.status_code})")
                return False
        except Exception as e:
            print(f"[Lofter] 提交出错: {e}")
            return False
    
    def run(self, max_pages: int = 3):
        """运行爬虫"""
        print("[Lofter] 开始爬取...")
        
        total_submitted = 0
        
        for keyword in self.keywords:
            keyword = keyword.strip()
            if not keyword:
                continue
            
            results = self.search(keyword, max_pages)
            
            for content in results:
                if self.submit_to_backend(content):
                    total_submitted += 1
                time.sleep(0.3)
        
        print(f"[Lofter] 爬取完成，共提交 {total_submitted} 个内容")


if __name__ == '__main__':
    spider = LofterSpider()
    spider.run(max_pages=2)
