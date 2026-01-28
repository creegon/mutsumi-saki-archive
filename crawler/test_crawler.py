"""测试 Lofter 爬虫"""
from lofter_crawler import get_html, get_session, get_post_info
import re

session = get_session()

# 测试用户页面
print("=" * 50)
print("测试用户页面爬取")
print("=" * 50)

html = get_html('https://coldiron.lofter.com/', session)
if html:
    print(f"页面长度: {len(html)}")
    
    # 查看页面内容的一部分
    print("\n页面内容片段:")
    print(html[:2000])
    
    # 找帖子链接
    pattern = r'lofter\.com/post/[0-9a-f]+_[0-9a-f]+'
    posts = re.findall(pattern, html)
    print(f"\n找到帖子数: {len(set(posts))}")
    for p in list(set(posts))[:5]:
        print(f"  https://{p}")
