"""
Yande.re / Konachan 爬虫 - 睦祥CP图专用
只爬取同时包含 wakaba_mutsumi 和 togawa_sakiko 的图
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# ============ 配置 ============
# Yande.re API (Moebooru)
YANDERE_API = "https://yande.re/post.json"
KONACHAN_API = "https://konachan.com/post.json"

# 搜索 tag - 两人CP
TAGS = "wakaba_mutsumi togawa_sakiko"

# API 配置
API_URL = os.environ.get('API_URL', 'http://localhost:3001/api')
API_TOKEN = os.environ.get('API_TOKEN', '')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# ============ 爬虫函数 ============

def fetch_posts(api_url: str, tags: str, limit: int = 100, page: int = 1) -> List[Dict]:
    """从 API 获取帖子列表"""
    params = {
        'tags': tags,
        'limit': limit,
        'page': page,
    }
    
    try:
        r = requests.get(api_url, params=params, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"[!] API 错误: {r.status_code}")
            return []
    except Exception as e:
        print(f"[!] 请求失败: {e}")
        return []

def crawl_yandere(max_pages: int = 5) -> List[Dict]:
    """爬取 Yande.re"""
    print(f"[*] 开始爬取 Yande.re - Tags: {TAGS}")
    
    all_posts = []
    
    for page in range(1, max_pages + 1):
        print(f"[*] 第 {page} 页...")
        posts = fetch_posts(YANDERE_API, TAGS, limit=100, page=page)
        
        if not posts:
            print(f"[*] 第 {page} 页没有内容，结束")
            break
        
        all_posts.extend(posts)
        print(f"    找到 {len(posts)} 张图")
    
    return all_posts

def crawl_konachan(max_pages: int = 5) -> List[Dict]:
    """爬取 Konachan"""
    print(f"\n[*] 开始爬取 Konachan - Tags: {TAGS}")
    
    all_posts = []
    
    for page in range(1, max_pages + 1):
        print(f"[*] 第 {page} 页...")
        posts = fetch_posts(KONACHAN_API, TAGS, limit=100, page=page)
        
        if not posts:
            print(f"[*] 第 {page} 页没有内容，结束")
            break
        
        all_posts.extend(posts)
        print(f"    找到 {len(posts)} 张图")
    
    return all_posts

def process_posts(posts: List[Dict], source: str) -> List[Dict]:
    """处理帖子数据，转换为统一格式"""
    results = []
    
    for post in posts:
        # 获取最高质量图片
        image_url = post.get('file_url') or post.get('jpeg_url') or post.get('sample_url')
        
        if not image_url:
            continue
        
        # 构建数据
        data = {
            'title': f"{source} #{post['id']}",
            'author': post.get('author', 'Unknown'),
            'url': f"https://yande.re/post/show/{post['id']}" if source == 'YANDERE' else f"https://konachan.com/post/show/{post['id']}",
            'images': [image_url],
            'tags': post.get('tags', '').split(),
            'rating': post.get('rating', 's'),
            'score': post.get('score', 0),
            'source_pixiv': post.get('source', ''),  # 通常包含 Pixiv 原链接
        }
        
        results.append(data)
    
    return results

def save_to_api(posts: List[Dict], source: str):
    """保存到后端 API"""
    if not API_TOKEN:
        print("[!] 未设置 API_TOKEN，跳过 API 保存")
        return
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }
    
    saved, skipped, failed = 0, 0, 0
    
    for post in posts:
        # 过滤 NSFW (rating: s=safe, q=questionable, e=explicit)
        if post.get('rating') == 'e':
            continue
        
        data = {
            'type': 'IMAGE',
            'source': source,
            'sourceUrl': post['url'],
            'title': post['title'],
            'authorName': post['author'],
            'images': post['images'],
            'tags': [t for t in post['tags'] if len(t) < 50][:20],  # 限制 tag 数量
        }
        
        try:
            r = requests.post(f'{API_URL}/content', json=data, headers=headers, timeout=30)
            if r.status_code == 201:
                saved += 1
                print(f"[+] {post['title']}")
            elif r.status_code == 409:
                skipped += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"[!] 错误: {e}")
    
    print(f"\n[*] {source}: 保存 {saved}, 跳过 {skipped}, 失败 {failed}")

def save_to_local(posts: List[Dict], filename: str):
    """保存到本地文件"""
    output = Path('output')
    output.mkdir(exist_ok=True)
    
    with open(output / filename, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    
    print(f"[*] 保存到 output/{filename}")

# ============ 主程序 ============

def main():
    print("=" * 50)
    print("  Yande.re / Konachan 爬虫")
    print("  睦祥 CP 图专用")
    print("  Tags: wakaba_mutsumi + togawa_sakiko")
    print("=" * 50)
    print()
    
    # 爬取 Yande.re
    yandere_raw = crawl_yandere(max_pages=10)
    yandere_posts = process_posts(yandere_raw, 'YANDERE')
    
    # 爬取 Konachan
    konachan_raw = crawl_konachan(max_pages=10)
    konachan_posts = process_posts(konachan_raw, 'KONACHAN')
    
    # 合并结果
    all_posts = yandere_posts + konachan_posts
    
    # 去重 (基于图片 URL)
    seen_urls = set()
    unique_posts = []
    for post in all_posts:
        url = post['images'][0]
        if url not in seen_urls:
            seen_urls.add(url)
            unique_posts.append(post)
    
    print(f"\n[*] 总计: {len(unique_posts)} 张图 (去重后)")
    print(f"    - Yande.re: {len(yandere_posts)}")
    print(f"    - Konachan: {len(konachan_posts)}")
    
    # 统计 rating
    safe = len([p for p in unique_posts if p.get('rating') == 's'])
    questionable = len([p for p in unique_posts if p.get('rating') == 'q'])
    explicit = len([p for p in unique_posts if p.get('rating') == 'e'])
    print(f"    - Safe: {safe}, Questionable: {questionable}, Explicit: {explicit}")
    
    if not unique_posts:
        print("[!] 没有找到任何图片")
        return
    
    # 保存选项
    print("\n保存方式:")
    print("1. 保存到 API")
    print("2. 保存到本地 JSON")
    print("3. 两者都保存")
    
    choice = input("选择 (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        save_to_api(unique_posts, 'YANDERE')
    
    if choice in ['2', '3']:
        filename = f"booru_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_to_local(unique_posts, filename)
    
    print("\n[*] 完成!")

if __name__ == '__main__':
    main()
