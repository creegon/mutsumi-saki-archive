#!/usr/bin/env python
"""
Pixiv OAuth Token 获取工具
运行后会打开浏览器登录 Pixiv，登录后从 URL 中获取 code 并输入
"""

from argparse import ArgumentParser
from base64 import urlsafe_b64encode
from hashlib import sha256
from pprint import pprint
from secrets import token_urlsafe
from sys import exit
from urllib.parse import urlencode
from webbrowser import open as open_url
import requests

USER_AGENT = "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)"
REDIRECT_URI = "https://app-api.pixiv.net/web/v1/users/auth/pixiv/callback"
LOGIN_URL = "https://app-api.pixiv.net/web/v1/login"
AUTH_TOKEN_URL = "https://oauth.secure.pixiv.net/auth/token"
CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"


def s256(data):
    """S256 transformation method."""
    return urlsafe_b64encode(sha256(data).digest()).rstrip(b"=").decode("ascii")


def oauth_pkce(transform):
    """Proof Key for Code Exchange by OAuth Public Clients (RFC7636)."""
    code_verifier = token_urlsafe(32)
    code_challenge = transform(code_verifier.encode("ascii"))
    return code_verifier, code_challenge


def login():
    code_verifier, code_challenge = oauth_pkce(s256)
    login_params = {
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "client": "pixiv-android",
    }
    
    login_url = f"{LOGIN_URL}?{urlencode(login_params)}"
    print("\n" + "=" * 60)
    print("Pixiv OAuth 登录")
    print("=" * 60)
    print("\n1. 浏览器会自动打开 Pixiv 登录页面")
    print("2. 登录你的 Pixiv 账号")
    print("3. 登录成功后，页面会跳转到一个空白页或错误页")
    print("4. 从浏览器地址栏复制 URL")
    print("5. URL 格式类似: pixiv://...?code=XXXXXX")
    print("6. 复制 code= 后面的那一串字符（到 & 之前）")
    print("\n" + "=" * 60)
    
    open_url(login_url)
    
    try:
        code = input("\n请输入 code: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n取消操作")
        return
    
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
        headers={"User-Agent": USER_AGENT},
    )
    
    data = response.json()
    
    if "refresh_token" in data:
        print("\n" + "=" * 60)
        print("✅ 获取成功！")
        print("=" * 60)
        print(f"\nrefresh_token: {data['refresh_token']}")
        print(f"access_token:  {data['access_token']}")
        print(f"expires_in:    {data.get('expires_in', 0)} 秒")
        print("\n请将 refresh_token 添加到 .env 文件:")
        print(f'PIXIV_REFRESH_TOKEN={data["refresh_token"]}')
        print("=" * 60)
        
        # 自动更新 .env 文件
        update = input("\n是否自动更新 .env 文件? (y/n): ").strip().lower()
        if update == 'y':
            update_env_file(data['refresh_token'])
    else:
        print("\n❌ 获取失败:")
        pprint(data)
        exit(1)


def update_env_file(refresh_token):
    """更新 .env 文件"""
    import os
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    # 读取现有内容
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
    
    print(f"✅ 已更新 {env_path}")


def refresh(refresh_token):
    """使用 refresh_token 获取新的 access_token"""
    response = requests.post(
        AUTH_TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "include_policy": "true",
            "refresh_token": refresh_token,
        },
        headers={"User-Agent": USER_AGENT},
    )
    
    data = response.json()
    
    if "refresh_token" in data:
        print("✅ Token 刷新成功!")
        print(f"新 refresh_token: {data['refresh_token']}")
        print(f"access_token: {data['access_token']}")
    else:
        print("❌ 刷新失败:")
        pprint(data)


if __name__ == "__main__":
    parser = ArgumentParser(description="Pixiv OAuth Token 工具")
    parser.add_argument('--refresh', '-r', type=str, help='使用 refresh_token 刷新')
    
    args = parser.parse_args()
    
    if args.refresh:
        refresh(args.refresh)
    else:
        login()
