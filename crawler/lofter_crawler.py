"""
Lofter 爬虫 - 睦祥资源站专用
支持按用户和按Tag爬取
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import re
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

# ============ 配置 ============
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Lofter 需要登录才能搜索 tag，把你的 Cookie 放这里
# 登录 lofter.com 后，按 F12 -> Network -> 刷新 -> 点任意请求 -> 复制 Cookie
LOFTER_COOKIE = os.environ.get('LOFTER_COOKIE', '')

TIMEOUT = 30
MAX_WORKERS = 4  # 并发数，不要太高以免被封
REQUEST_DELAY = 1  # 请求间隔（秒）
DATE_DELTA = timedelta(days=40732)  # Lofter 时间戳偏移

# API 配置
API_URL = os.environ.get('API_URL', 'http://localhost:3001/api')
API_TOKEN = os.environ.get('API_TOKEN', '')

# ============ 工具函数 ============

def get_session() -> requests.Session:
    """创建带 Cookie 的 Session"""
    session = requests.Session()
    session.headers.update(HEADERS)
    if LOFTER_COOKIE:
        session.headers['Cookie'] = LOFTER_COOKIE
    return session

def get_html(url: str, session: requests.Session = None) -> Optional[str]:
    """获取页面 HTML"""
    if session is None:
        session = get_session()
    try:
        time.sleep(REQUEST_DELAY)
        r = session.get(url, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.text
        else:
            print(f'[!] 访问失败 ({r.status_code}): {url}')
            return None
    except Exception as e:
        print(f'[!] 请求错误: {e}')
        return None

def parse_post_date(url: str) -> str:
    """从帖子 URL 解析日期"""
    try:
        # URL 格式: xxx.lofter.com/post/1234_5678abcd
        hex_time = url.split('_')[-1]
        timestamp = int(hex_time, 16)
        date = datetime.fromtimestamp(timestamp) - DATE_DELTA
        return date.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')

def clean_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/:*?"<>|]', '_', name)[:100]

def get_image_original_url(url: str) -> str:
    """获取图片原图 URL"""
    # 移除尺寸限制参数，获取最大尺寸
    if '?' in url:
        base_url = url.split('?')[0]
        return f"{base_url}?imageView&thumbnail=0x0&quality=100&stripmeta=0"
    return url

# ============ 用户爬取 ============

def get_user_page_url(domain: str, page: int) -> str:
    """获取用户博客页面 URL"""
    if page == 1:
        return f'https://{domain}.lofter.com/'
    return f'https://{domain}.lofter.com/?page={page}'

def get_post_links_from_page(url: str, session: requests.Session) -> List[str]:
    """从页面获取所有帖子链接"""
    html = get_html(url, session)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    # 匹配帖子链接
    pattern = re.compile(r'https://[a-zA-Z0-9-]+\.lofter\.com/post/[0-9a-f]+_[0-9a-f]+')
    links = set()
    
    for a in soup.find_all('a', href=pattern):
        href = a.get('href')
        if href:
            links.add(href)
    
    return list(links)

def get_post_info(url: str, session: requests.Session) -> Optional[Dict]:
    """获取帖子详细信息"""
    html = get_html(url, session)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 标题
    title = soup.head.title.text.strip() if soup.head and soup.head.title else ''
    title = re.sub(r'\s+', ' ', title)
    
    # 作者
    author = ''
    author_link = soup.find('a', class_='personcardname')
    if author_link:
        author = author_link.text.strip()
    else:
        # 从 URL 提取
        match = re.search(r'https://([a-zA-Z0-9-]+)\.lofter\.com', url)
        if match:
            author = match.group(1)
    
    # 正文
    text_content = ''
    content_div = soup.find('div', class_='content') or soup.find('div', class_='text')
    if content_div:
        text_content = content_div.get_text(separator='\n', strip=True)
    
    # 图片
    images = []
    for img in soup.find_all(lambda tag: tag.has_attr('bigimgsrc')):
        img_url = img.get('bigimgsrc')
        if img_url:
            images.append(get_image_original_url(img_url))
    
    # 如果没找到 bigimgsrc，尝试其他方式
    if not images:
        for img in soup.find_all('img', src=re.compile(r'imglf\d*\.nosdn.*\.126\.net')):
            img_url = img.get('src')
            if img_url:
                images.append(get_image_original_url(img_url))
    
    # 标签
    tags = []
    for tag_link in soup.find_all('a', class_='tag'):
        tag_text = tag_link.text.strip()
        if tag_text:
            tags.append(tag_text)
    
    # 日期
    date = parse_post_date(url)
    
    return {
        'title': title,
        'author': author,
        'url': url,
        'date': date,
        'text': text_content,
        'images': images,
        'tags': tags,
    }

def crawl_user(domain: str, max_pages: int = 0) -> List[Dict]:
    """
    爬取用户的所有帖子
    
    Args:
        domain: 用户域名，如 'coldiron'
        max_pages: 最大页数，0 表示全部
    
    Returns:
        帖子信息列表
    """
    print(f'[*] 开始爬取用户: {domain}')
    session = get_session()
    
    # 收集所有帖子链接
    all_post_links = []
    page = 1
    
    while True:
        url = get_user_page_url(domain, page)
        print(f'[*] 正在获取第 {page} 页...')
        
        links = get_post_links_from_page(url, session)
        if not links:
            print(f'[*] 第 {page} 页没有内容，结束')
            break
        
        all_post_links.extend(links)
        page += 1
        
        if max_pages and page > max_pages:
            break
    
    # 去重
    all_post_links = list(set(all_post_links))
    print(f'[*] 共找到 {len(all_post_links)} 个帖子')
    
    # 获取每个帖子的详细信息
    posts = []
    for i, link in enumerate(all_post_links):
        print(f'[*] 获取帖子 ({i+1}/{len(all_post_links)}): {link}')
        post_info = get_post_info(link, session)
        if post_info:
            posts.append(post_info)
    
    return posts

# ============ Tag 爬取 ============

def get_tag_api_url(tag: str, page: int = 1) -> str:
    """获取 Tag 搜索 API URL"""
    encoded_tag = quote(tag)
    # Lofter 的 tag 页面使用 AJAX 加载
    return f'https://www.lofter.com/tag/{encoded_tag}?page={page}'

def crawl_tag_page(tag: str, page: int, session: requests.Session) -> List[str]:
    """爬取 Tag 页面的帖子链接"""
    url = get_tag_api_url(tag, page)
    html = get_html(url, session)
    
    if not html:
        return []
    
    # 检查是否需要登录
    if '登录' in html and 'login' in html.lower():
        print('[!] 需要登录才能访问 Tag 页面，请设置 LOFTER_COOKIE')
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    pattern = re.compile(r'https://[a-zA-Z0-9-]+\.lofter\.com/post/[0-9a-f]+_[0-9a-f]+')
    links = set()
    
    for a in soup.find_all('a', href=pattern):
        href = a.get('href')
        if href:
            links.add(href)
    
    return list(links)

def crawl_tag(tag: str, max_pages: int = 10) -> List[Dict]:
    """
    按 Tag 爬取帖子
    
    Args:
        tag: 标签名，如 '睦祥'
        max_pages: 最大页数
    
    Returns:
        帖子信息列表
    """
    if not LOFTER_COOKIE:
        print('[!] 警告: 未设置 LOFTER_COOKIE，Tag 爬取可能失败')
    
    print(f'[*] 开始爬取 Tag: {tag}')
    session = get_session()
    
    all_post_links = []
    
    for page in range(1, max_pages + 1):
        print(f'[*] 正在获取第 {page} 页...')
        links = crawl_tag_page(tag, page, session)
        
        if not links:
            print(f'[*] 第 {page} 页没有内容，结束')
            break
        
        all_post_links.extend(links)
        print(f'    找到 {len(links)} 个帖子')
    
    # 去重
    all_post_links = list(set(all_post_links))
    print(f'[*] 共找到 {len(all_post_links)} 个帖子')
    
    # 获取每个帖子的详细信息
    posts = []
    for i, link in enumerate(all_post_links):
        print(f'[*] 获取帖子 ({i+1}/{len(all_post_links)}): {link}')
        post_info = get_post_info(link, session)
        if post_info and post_info['images']:  # 只保留有图片的
            posts.append(post_info)
    
    return posts

# ============ 保存到 API ============

def save_to_api(posts: List[Dict], source: str = 'LOFTER'):
    """将爬取结果保存到后端 API"""
    if not API_TOKEN:
        print('[!] 未设置 API_TOKEN，跳过保存到 API')
        return
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }
    
    saved = 0
    skipped = 0
    
    for post in posts:
        if not post['images']:
            continue
        
        data = {
            'type': 'IMAGE',
            'source': source,
            'sourceUrl': post['url'],
            'title': post['title'],
            'authorName': post['author'],
            'images': post['images'],
            'textContent': post.get('text', ''),
            'tags': post.get('tags', []),
        }
        
        try:
            r = requests.post(f'{API_URL}/content', json=data, headers=headers, timeout=30)
            if r.status_code == 201:
                saved += 1
                print(f'[+] 保存成功: {post["title"][:30]}...')
            elif r.status_code == 409:
                skipped += 1
                print(f'[-] 已存在: {post["title"][:30]}...')
            else:
                print(f'[!] 保存失败 ({r.status_code}): {post["title"][:30]}...')
        except Exception as e:
            print(f'[!] API 错误: {e}')
    
    print(f'\n[*] 完成！保存 {saved} 个，跳过 {skipped} 个')

# ============ 保存到本地 ============

def save_to_local(posts: List[Dict], output_dir: str = 'output'):
    """将爬取结果保存到本地"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 保存 JSON
    json_file = output_path / f'lofter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    
    print(f'[*] 已保存到 {json_file}')
    
    # 下载图片
    download_images = input('[?] 是否下载图片到本地? (y/n): ').strip().lower() == 'y'
    if download_images:
        images_dir = output_path / 'images'
        images_dir.mkdir(exist_ok=True)
        
        session = get_session()
        for post in posts:
            for i, img_url in enumerate(post['images']):
                try:
                    filename = f"{clean_filename(post['author'])}_{post['date']}_{i+1}.jpg"
                    filepath = images_dir / filename
                    
                    if filepath.exists():
                        continue
                    
                    print(f'[*] 下载: {filename}')
                    r = session.get(img_url, timeout=60)
                    if r.status_code == 200:
                        with open(filepath, 'wb') as f:
                            f.write(r.content)
                except Exception as e:
                    print(f'[!] 下载失败: {e}')

# ============ 主程序 ============

def main():
    print('=' * 50)
    print('  Lofter 爬虫 - 睦祥资源站专用')
    print('=' * 50)
    print()
    print('选择爬取模式:')
    print('1. 按用户爬取')
    print('2. 按 Tag 爬取')
    print()
    
    mode = input('请选择 (1/2): ').strip()
    
    posts = []
    
    if mode == '1':
        domain = input('请输入用户域名 (如 coldiron): ').strip()
        max_pages = input('最大页数 (0=全部): ').strip()
        max_pages = int(max_pages) if max_pages else 0
        posts = crawl_user(domain, max_pages)
    
    elif mode == '2':
        tag = input('请输入 Tag (如 睦祥): ').strip()
        max_pages = input('最大页数 (默认10): ').strip()
        max_pages = int(max_pages) if max_pages else 10
        posts = crawl_tag(tag, max_pages)
    
    else:
        print('[!] 无效选择')
        return
    
    if not posts:
        print('[!] 没有找到任何帖子')
        return
    
    print(f'\n[*] 共获取 {len(posts)} 个帖子')
    print()
    print('保存方式:')
    print('1. 保存到后端 API')
    print('2. 保存到本地文件')
    print('3. 两者都保存')
    
    save_mode = input('请选择 (1/2/3): ').strip()
    
    if save_mode in ['1', '3']:
        save_to_api(posts)
    
    if save_mode in ['2', '3']:
        save_to_local(posts)
    
    print('\n[*] 完成！')

if __name__ == '__main__':
    main()
