#!/usr/bin/env python
"""
Pixiv OAuth Token 自动获取工具 (简洁版)
使用全新的 Chrome 实例，避免配置冲突
"""

import os
import sys
import time
import json
import re
from base64 import urlsafe_b64encode
from hashlib import sha256
from secrets import token_urlsafe
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

USER_AGENT = "PixivIOSApp/7.13.3 (iOS 14.6; iPhone13,2)"
REDIRECT_URI = "https://app-api.pixiv.net/web/v1/users/auth/pixiv/callback"
LOGIN_URL = "https://app-api.pixiv.net/web/v1/login"
AUTH_TOKEN_URL = "https://oauth.secure.pixiv.net/auth/token"
CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"


def s256(data):
    return urlsafe_b64encode(sha256(data).digest()).rstrip(b"=").decode("ascii")


def oauth_pkce(transform):
    code_verifier = token_urlsafe(32)
    code_challenge = transform(code_verifier.encode("ascii"))
    return code_verifier, code_challenge


def update_env_file(refresh_token):
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    lines = []
    token_found = False
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('PIXIV_REFRESH_TOKEN='):
                    lines.append(f'PIXIV_REFRESH_TOKEN={refresh_token}\n')
                    token_found = True
                else:
                    lines.append(line)
    
    if not token_found:
        lines.append(f'PIXIV_REFRESH_TOKEN={refresh_token}\n')
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"[OK] Token 已保存到 {env_path}")


def login_clean():
    """使用干净的 Chrome 实例"""
    print("\n" + "=" * 60)
    print("Pixiv OAuth 自动登录")
    print("=" * 60)
    
    code_verifier, code_challenge = oauth_pkce(s256)
    print(f"[INFO] code_verifier: {code_verifier[:20]}...")
    
    login_params = {
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "client": "pixiv-android",
    }
    login_url = f"{LOGIN_URL}?{urlencode(login_params)}"
    
    print("[INFO] 启动 Chrome...")
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # 隐藏 webdriver 特征
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    try:
        print("[INFO] 打开 Pixiv 登录页面...")
        driver.get(login_url)
        
        print("\n" + "=" * 60)
        print("请在浏览器中登录 Pixiv:")
        print("  邮箱: hl2595@cornell.edu")
        print("  密码: creegon123")
        print("")
        print("注意：请使用「邮箱地址或pixiv ID」登录")
        print("      不要使用 Google/Apple/Twitter 登录！")
        print("=" * 60 + "\n")
        
        # 等待登录完成
        max_wait = 300
        start_time = time.time()
        last_url = ""
        
        while time.time() - start_time < max_wait:
            current_url = driver.current_url
            
            if current_url != last_url:
                print(f"[DEBUG] URL: {current_url[:60]}...")
                last_url = current_url
            
            if "post-redirect" in current_url:
                print("[INFO] 检测到登录完成！")
                time.sleep(3)
                break
            
            time.sleep(1)
        else:
            print("[ERROR] 登录超时")
            return None
        
        # 从性能日志中提取 code
        code = None
        print("[INFO] 正在从网络日志中提取 code...")
        
        for entry in driver.get_log("performance"):
            try:
                message = json.loads(entry["message"])["message"]
                if message.get("method") == "Network.requestWillBeSent":
                    url = message.get("params", {}).get("documentURL", "")
                    if url.startswith("pixiv://") and "code=" in url:
                        match = re.search(r'code=([^&]+)', url)
                        if match:
                            code = match.group(1)
                            print(f"[INFO] 找到 code!")
                            break
            except:
                continue
        
        if code:
            return code, code_verifier
        else:
            print("[ERROR] 未能提取 code")
            print("[INFO] 请手动检查浏览器开发者工具的网络请求...")
            input("按 Enter 关闭...")
            return None
        
    finally:
        driver.quit()


def exchange_token(code, code_verifier):
    print("[INFO] 正在获取 Token...")
    
    response = requests.post(
        AUTH_TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "code_verifier": code_verifier,
            "grant_type": "authorization_code",
            "include_policy": "true",
            "redirect_uri": REDIRECT_URI,
        },
        headers={
            "User-Agent": USER_AGENT,
            "app-os-version": "14.6",
            "app-os": "ios",
        },
    )
    
    data = response.json()
    
    if "refresh_token" in data:
        print("\n" + "=" * 60)
        print("[OK] Token 获取成功!")
        print("=" * 60)
        print(f"refresh_token: {data['refresh_token']}")
        print("=" * 60)
        
        update_env_file(data['refresh_token'])
        return data['refresh_token']
    else:
        print("[ERROR] 获取 Token 失败:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return None


if __name__ == "__main__":
    result = login_clean()
    if result:
        code, code_verifier = result
        exchange_token(code, code_verifier)
