"""
Pixiv Spider for MutsumiSaki Archive
爬取 Pixiv 上的睦祥相关插画和小说
"""
import os
import sys
import time
import json
from datetime import datetime
from typing import Optional, List
from pixivpy3 import AppPixivAPI
import requests
from dotenv import load_dotenv

# 解决 Windows 终端编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()


class PixivSpider:
    def __init__(self, backend_url: str = None):
        self.api = AppPixivAPI()
        self.backend_url = backend_url or os.getenv('BACKEND_URL', 'http://localhost:3001/api')
        self.keywords = os.getenv('KEYWORDS', '睦祥,祥睦').split(',')
        self.logged_in = False
        self.stats = {'illusts': 0, 'novels': 0, 'skipped': 0, 'errors': 0}
        
    def login(self) -> bool:
        """登录 Pixiv（使用 refresh token）"""
        refresh_token = os.getenv('PIXIV_REFRESH_TOKEN')
        
        if not refresh_token:
            print("[Pixiv] 错误: 未找到 PIXIV_REFRESH_TOKEN")
            print("[Pixiv] 请运行 python get_pixiv_token.py 获取 token")
            return False
        
        try:
            print("[Pixiv] 使用 refresh_token 登录...")
            self.api.auth(refresh_token=refresh_token)
            self.logged_in = True
            print("[Pixiv] 登录成功!")
            return True
        except Exception as e:
            print(f"[Pixiv] 登录失败: {e}")
            return False
    
    def check_exists(self, source_url: str) -> bool:
        """检查内容是否已存在"""
        try:
            resp = requests.get(
                f'{self.backend_url}/content',
                params={'search': source_url, 'limit': 1},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get('items') and len(data['items']) > 0:
                    return True
            return False
        except:
            return False
    
    def search_illusts(self, keyword: str, max_pages: int = 5) -> List[dict]:
        """搜索插画"""
        if not self.logged_in:
            print("[Pixiv] 未登录，无法搜索")
            return []
        
        results = []
        offset = 0
        
        for page in range(max_pages):
            try:
                print(f"[Pixiv] 搜索插画 '{keyword}' 第 {page + 1}/{max_pages} 页...")
                resp = self.api.search_illust(keyword, offset=offset)
                
                if not resp.illusts:
                    print(f"[Pixiv] 关键词 '{keyword}' 插画搜索完毕")
                    break
                
                for illust in resp.illusts:
                    content = self._parse_illust(illust)
                    if content:
                        # 检查是否已存在
                        if self.check_exists(content['sourceUrl']):
                            self.stats['skipped'] += 1
                            continue
                        results.append(content)
                
                offset += 30
                time.sleep(1)  # 避免请求过快
                
            except Exception as e:
                print(f"[Pixiv] 搜索出错: {e}")
                self.stats['errors'] += 1
                break
        
        print(f"[Pixiv] 关键词 '{keyword}' 找到 {len(results)} 个新插画")
        return results
    
    def search_novels(self, keyword: str, max_pages: int = 5) -> List[dict]:
        """搜索小说"""
        if not self.logged_in:
            print("[Pixiv] 未登录，无法搜索")
            return []
        
        results = []
        offset = 0
        
        for page in range(max_pages):
            try:
                print(f"[Pixiv] 搜索小说 '{keyword}' 第 {page + 1}/{max_pages} 页...")
                resp = self.api.search_novel(keyword, offset=offset)
                
                if not resp.novels:
                    print(f"[Pixiv] 关键词 '{keyword}' 小说搜索完毕")
                    break
                
                for novel in resp.novels:
                    source_url = f'https://www.pixiv.net/novel/show.php?id={novel.id}'
                    
                    # 检查是否已存在
                    if self.check_exists(source_url):
                        self.stats['skipped'] += 1
                        continue
                    
                    content = self._parse_novel(novel)
                    if content:
                        results.append(content)
                
                offset += 30
                time.sleep(1)
                
            except Exception as e:
                print(f"[Pixiv] 搜索小说出错: {e}")
                self.stats['errors'] += 1
                break
        
        print(f"[Pixiv] 关键词 '{keyword}' 找到 {len(results)} 篇新小说")
        return results
    
    def get_novel_text(self, novel_id: int) -> Optional[str]:
        """获取小说正文"""
        try:
            resp = self.api.novel_text(novel_id)
            if resp and hasattr(resp, 'novel_text'):
                return resp.novel_text
            return None
        except Exception as e:
            print(f"[Pixiv] 获取小说正文出错 ({novel_id}): {e}")
            return None
    
    def _parse_illust(self, illust) -> Optional[dict]:
        """解析插画数据"""
        try:
            # 获取图片 URL
            images = []
            if illust.meta_single_page.get('original_image_url'):
                images.append(illust.meta_single_page['original_image_url'])
            elif illust.meta_pages:
                for page in illust.meta_pages:
                    img_url = page.image_urls.get('original') or page.image_urls.get('large')
                    if img_url:
                        images.append(img_url)
            else:
                img_url = illust.image_urls.get('large') or illust.image_urls.get('medium')
                if img_url:
                    images.append(img_url)
            
            if not images:
                return None
            
            # 确定类型
            content_type = 'MANGA' if illust.type == 'manga' else 'IMAGE'
            
            # 提取标签
            tags = [tag.name for tag in illust.tags]
            
            return {
                'type': content_type,
                'source': 'PIXIV',
                'sourceUrl': f'https://www.pixiv.net/artworks/{illust.id}',
                'sourceId': str(illust.id),
                'title': illust.title,
                'authorName': illust.user.name,
                'authorId': str(illust.user.id),
                'images': images,
                'textContent': illust.caption or '',
                'tags': tags,
                'publishedAt': illust.create_date,
            }
        except Exception as e:
            print(f"[Pixiv] 解析插画出错: {e}")
            return None
    
    def _parse_novel(self, novel) -> Optional[dict]:
        """解析小说数据"""
        try:
            # 提取标签
            tags = [tag.name for tag in novel.tags]
            
            # 获取封面图
            cover_image = novel.image_urls.get('large') or novel.image_urls.get('medium')
            images = [cover_image] if cover_image else []
            
            # 获取完整正文
            print(f"[Pixiv] 获取小说正文: {novel.title[:30]}...")
            full_text = self.get_novel_text(novel.id)
            time.sleep(0.5)  # 避免请求过快
            
            # 构建内容：简介 + 正文
            text_content = ""
            if novel.caption:
                text_content += f"【简介】\n{novel.caption}\n\n"
            if full_text:
                text_content += f"【正文】\n{full_text}"
            else:
                text_content += f"【简介】\n{novel.caption or '无'}"
            
            return {
                'type': 'TEXT',
                'source': 'PIXIV',
                'sourceUrl': f'https://www.pixiv.net/novel/show.php?id={novel.id}',
                'sourceId': str(novel.id),
                'title': novel.title,
                'authorName': novel.user.name,
                'authorId': str(novel.user.id),
                'images': images,
                'textContent': text_content,
                'tags': tags,
                'publishedAt': novel.create_date,
            }
        except Exception as e:
            print(f"[Pixiv] 解析小说出错: {e}")
            return None
    
    def submit_to_backend(self, content: dict) -> bool:
        """提交内容到后端 API"""
        try:
            resp = requests.post(
                f'{self.backend_url}/content',
                json=content,
                timeout=30
            )
            if resp.status_code in [200, 201]:
                content_type = '插画' if content['type'] == 'IMAGE' else '漫画' if content['type'] == 'MANGA' else '小说'
                print(f"[Pixiv] ✓ {content_type}: {content['title'][:40]}")
                return True
            elif resp.status_code == 409:
                self.stats['skipped'] += 1
                return True
            else:
                print(f"[Pixiv] ✗ 提交失败 ({resp.status_code}): {content['title'][:30]}")
                self.stats['errors'] += 1
                return False
        except Exception as e:
            print(f"[Pixiv] ✗ 提交出错: {e}")
            self.stats['errors'] += 1
            return False
    
    def run(self, max_pages: int = 3, include_novels: bool = True):
        """运行爬虫"""
        print("\n" + "=" * 60)
        print("Pixiv 爬虫 - 开始运行")
        print(f"关键词: {', '.join(self.keywords)}")
        print(f"每个关键词最大页数: {max_pages}")
        print(f"爬取小说: {'是' if include_novels else '否'}")
        print("=" * 60 + "\n")
        
        if not self.login():
            print("[Pixiv] 登录失败，停止爬取")
            return
        
        for keyword in self.keywords:
            keyword = keyword.strip()
            if not keyword:
                continue
            
            print(f"\n[Pixiv] 处理关键词: {keyword}")
            print("-" * 40)
            
            # 搜索并提交插画
            illusts = self.search_illusts(keyword, max_pages)
            for content in illusts:
                if self.submit_to_backend(content):
                    self.stats['illusts'] += 1
                time.sleep(0.3)
            
            # 搜索并提交小说
            if include_novels:
                novels = self.search_novels(keyword, max_pages)
                for content in novels:
                    if self.submit_to_backend(content):
                        self.stats['novels'] += 1
                    time.sleep(0.3)
        
        print("\n" + "=" * 60)
        print("Pixiv 爬虫 - 运行完成")
        print(f"新增插画: {self.stats['illusts']}")
        print(f"新增小说: {self.stats['novels']}")
        print(f"跳过(已存在): {self.stats['skipped']}")
        print(f"错误: {self.stats['errors']}")
        print("=" * 60 + "\n")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Pixiv 爬虫')
    parser.add_argument('--pages', '-p', type=int, default=3, help='每个关键词最大页数')
    parser.add_argument('--no-novels', action='store_true', help='不爬取小说')
    
    args = parser.parse_args()
    
    spider = PixivSpider()
    spider.run(max_pages=args.pages, include_novels=not args.no_novels)
