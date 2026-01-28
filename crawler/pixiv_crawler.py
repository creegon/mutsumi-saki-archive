#!/usr/bin/env python3
"""
Pixiv Crawler for MutsumiSaki Archive
Extracts cookies from Chrome automatically
"""

import os
import re
import json
import time
import sys
import requests
import browser_cookie3
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# API endpoints
PIXIV_AJAX_SEARCH = "https://www.pixiv.net/ajax/search/artworks/{keyword}?word={keyword}&order=date_d&mode=all&p={page}&s_mode=s_tag&type=all&lang=ja"
PIXIV_AJAX_ILLUST = "https://www.pixiv.net/ajax/illust/{illust_id}"
PIXIV_AJAX_PAGES = "https://www.pixiv.net/ajax/illust/{illust_id}/pages"

# Backend API
BACKEND_API = os.getenv("BACKEND_API", "http://localhost:3001/api")

class PixivCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.pixiv.net/",
            "Accept": "application/json",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        })
        self._load_cookies()
    
    def _load_cookies(self):
        """Load cookies from Chrome browser"""
        try:
            print("[COOKIE] Loading cookies from Chrome...")
            cj = browser_cookie3.chrome(domain_name=".pixiv.net")
            self.session.cookies.update(cj)
            
            # Check if PHPSESSID exists
            cookies_dict = {c.name: c.value for c in self.session.cookies}
            if "PHPSESSID" in cookies_dict:
                print(f"[OK] Found PHPSESSID: {cookies_dict['PHPSESSID'][:20]}...")
            else:
                print("[WARN] PHPSESSID not found - you may need to login to Pixiv in Chrome")
                
        except Exception as e:
            print(f"[ERROR] Failed to load cookies: {e}")
            print("[TIP] Make sure Chrome is closed or try running as administrator")
    
    def search(self, keyword: str, max_pages: int = 3) -> list:
        """Search artworks by keyword"""
        results = []
        encoded_keyword = quote(keyword)
        
        for page in range(1, max_pages + 1):
            url = PIXIV_AJAX_SEARCH.format(keyword=encoded_keyword, page=page)
            print(f"[SEARCH] Page {page}: {keyword}")
            
            try:
                resp = self.session.get(url, timeout=30)
                data = resp.json()
                
                if data.get("error"):
                    print(f"[ERROR] API Error: {data.get('message')}")
                    break
                
                illusts = data.get("body", {}).get("illustManga", {}).get("data", [])
                if not illusts:
                    print(f"[INFO] No more results on page {page}")
                    break
                
                for illust in illusts:
                    results.append({
                        "id": illust.get("id"),
                        "title": illust.get("title"),
                        "author": illust.get("userName"),
                        "author_id": illust.get("userId"),
                        "tags": illust.get("tags", []),
                        "thumb": illust.get("url"),
                    })
                
                print(f"[OK] Found {len(illusts)} artworks on page {page}")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"[ERROR] Error on page {page}: {e}")
                break
        
        return results
    
    def get_illust_details(self, illust_id: str) -> dict:
        """Get full details for an illustration"""
        url = PIXIV_AJAX_ILLUST.format(illust_id=illust_id)
        
        try:
            resp = self.session.get(url, timeout=30)
            data = resp.json()
            
            if data.get("error"):
                return None
            
            body = data.get("body", {})
            return {
                "id": body.get("id"),
                "title": body.get("title"),
                "description": body.get("description"),
                "author": body.get("userName"),
                "author_id": body.get("userId"),
                "tags": [t.get("tag") for t in body.get("tags", {}).get("tags", [])],
                "like_count": body.get("likeCount", 0),
                "bookmark_count": body.get("bookmarkCount", 0),
                "view_count": body.get("viewCount", 0),
                "create_date": body.get("createDate"),
                "page_count": body.get("pageCount", 1),
            }
        except Exception as e:
            print(f"[ERROR] Error getting illust {illust_id}: {e}")
            return None
    
    def get_image_urls(self, illust_id: str) -> list:
        """Get original image URLs for an illustration"""
        url = PIXIV_AJAX_PAGES.format(illust_id=illust_id)
        
        try:
            resp = self.session.get(url, timeout=30)
            data = resp.json()
            
            if data.get("error"):
                return []
            
            return [
                page.get("urls", {}).get("original") or page.get("urls", {}).get("regular")
                for page in data.get("body", [])
            ]
        except Exception as e:
            print(f"[ERROR] Error getting pages for {illust_id}: {e}")
            return []
    
    def save_to_backend(self, illust: dict, images: list) -> bool:
        """Save artwork to backend API"""
        try:
            payload = {
                "type": "IMAGE",
                "source": "PIXIV",
                "sourceUrl": f"https://www.pixiv.net/artworks/{illust['id']}",
                "sourceId": str(illust['id']),
                "title": illust.get("title", ""),
                "authorName": illust.get("author", ""),
                "authorId": illust.get("author_id", ""),
                "images": images,
                "tags": illust.get("tags", []),
                "likes": illust.get("bookmark_count", 0),
            }
            
            resp = requests.post(f"{BACKEND_API}/content", json=payload, timeout=10)
            if resp.status_code in (200, 201):
                print(f"[SAVED] {illust.get('title')}")
                return True
            else:
                print(f"[WARN] Backend error: {resp.text}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to save: {e}")
            return False
    
    def crawl(self, keywords: list, max_pages: int = 3):
        """Main crawl function"""
        total_saved = 0
        
        for keyword in keywords:
            print(f"\n{'='*50}")
            print(f"[TARGET] Crawling: {keyword}")
            print(f"{'='*50}")
            
            results = self.search(keyword, max_pages)
            print(f"[STATS] Found {len(results)} artworks for '{keyword}'")
            
            for i, item in enumerate(results):
                print(f"\n[{i+1}/{len(results)}] Processing: {item['title']}")
                
                # Get details
                details = self.get_illust_details(item['id'])
                if not details:
                    continue
                
                # Get image URLs
                images = self.get_image_urls(item['id'])
                if not images:
                    print(f"  [WARN] No images found")
                    continue
                
                print(f"  [IMG] {len(images)} image(s)")
                print(f"  [LIKE] {details.get('bookmark_count', 0)} bookmarks")
                
                # Save to backend
                if self.save_to_backend(details, images):
                    total_saved += 1
                
                time.sleep(0.5)  # Rate limiting
        
        print(f"\n{'='*50}")
        print(f"[DONE] Crawl complete! Saved {total_saved} artworks")
        print(f"{'='*50}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Pixiv Crawler")
    parser.add_argument("--keywords", "-k", nargs="+", default=["若葉睦", "豊川祥子", "睦祥"],
                        help="Keywords to search")
    parser.add_argument("--pages", "-p", type=int, default=2,
                        help="Max pages per keyword")
    parser.add_argument("--test", "-t", action="store_true",
                        help="Test mode - just check cookies")
    args = parser.parse_args()
    
    crawler = PixivCrawler()
    
    if args.test:
        print("\n[TEST] Testing connection...")
        results = crawler.search("若葉睦", max_pages=1)
        if results:
            print(f"[OK] Test successful! Found {len(results)} results")
            print(f"   First result: {results[0]['title']}")
        else:
            print("[ERROR] Test failed - check your login")
    else:
        crawler.crawl(args.keywords, args.pages)


if __name__ == "__main__":
    main()
