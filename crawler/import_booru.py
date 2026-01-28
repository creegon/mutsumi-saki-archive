"""导入所有 Booru 数据到后端 - 不过滤 NSFW"""
import json
import requests

API_URL = "http://localhost:3001/api"

# 读取数据
with open('output/booru_20260128_161543.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

print(f"准备导入 {len(posts)} 条数据...")

saved, skipped, failed = 0, 0, 0

for post in posts:
    data = {
        'type': 'IMAGE',
        'source': 'YANDERE',
        'sourceUrl': post['url'],
        'title': post['title'],
        'authorName': post['author'],
        'images': post['images'],
        'tags': [t for t in post['tags'] if len(t) < 50][:20],
    }
    
    try:
        r = requests.post(f'{API_URL}/content', json=data, timeout=30)
        if r.status_code == 201:
            saved += 1
            print(f"[+] {post['title']}")
        elif r.status_code == 409:
            skipped += 1
        else:
            failed += 1
            print(f"[!] {r.status_code}: {post['title']}")
    except Exception as e:
        failed += 1
        print(f"[!] Error: {e}")

print(f"\n完成！保存: {saved}, 跳过: {skipped}, 失败: {failed}")

# 检查最终状态
r = requests.get(f'{API_URL}/content/stats')
print(f"当前统计: {r.json()}")
