"""
Twitter 批量爬取脚本
从 #むつさき tag 的 media 搜索结果提取内容
"""

import requests
import json
import time
from typing import List, Dict

BACKEND_URL = "http://localhost:3001"

def get_tweet_images(tweet_url: str, cookies: str) -> List[str]:
    """
    通过 Twitter embed API 获取推文图片
    这个方法比较可靠
    """
    # 使用 Twitter 的 publish API
    embed_url = f"https://publish.twitter.com/oembed?url={tweet_url}&omit_script=true"
    
    try:
        resp = requests.get(embed_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # 从 HTML 中提取图片
            html = data.get('html', '')
            # 简单返回，让前端代理处理
            return []
    except:
        pass
    
    return []


def submit_tweet(tweet: Dict) -> bool:
    """提交推文到后端"""
    body = {
        "type": "IMAGE",
        "source": "TWITTER", 
        "sourceUrl": tweet["url"],
        "sourceId": f"twitter_{tweet['tweetId']}",
        "title": f"Tweet by @{tweet['author']}",
        "authorName": tweet["author"],
        "images": tweet.get("images", []),
        "tags": ["むつさき", "mutsusaki", "twitter"]
    }
    
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/content",
            json=body,
            timeout=30
        )
        return resp.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {e}")
        return False


# 从媒体网格视图获取的推文列表
TWEETS = [
    {"author":"Saffron114214","tweetId":"1973331758776197360","url":"https://x.com/Saffron114214/status/1973331758776197360"},
    {"author":"NE2OP_","tweetId":"1974470499603464343","url":"https://x.com/NE2OP_/status/1974470499603464343"},
    {"author":"NE2OP_","tweetId":"1954378636800508316","url":"https://x.com/NE2OP_/status/1954378636800508316"},
    {"author":"NE2OP_","tweetId":"1974714195846615180","url":"https://x.com/NE2OP_/status/1974714195846615180"},
    {"author":"mokacoat_112233","tweetId":"1851255005862351143","url":"https://x.com/mokacoat_112233/status/1851255005862351143"},
    {"author":"nutella__1231","tweetId":"1918670365980508201","url":"https://x.com/nutella__1231/status/1918670365980508201"},
    {"author":"Umie_0909","tweetId":"1965699283958817276","url":"https://x.com/Umie_0909/status/1965699283958817276"},
    {"author":"22694BZ","tweetId":"1944015121208291731","url":"https://x.com/22694BZ/status/1944015121208291731"},
    {"author":"Dekamimi_1917","tweetId":"1904733208559968387","url":"https://x.com/Dekamimi_1917/status/1904733208559968387"},
    {"author":"TOTo_rabpit3","tweetId":"1997627414181224896","url":"https://x.com/TOTo_rabpit3/status/1997627414181224896"},
    {"author":"Tomagoooo","tweetId":"1977251676471107989","url":"https://x.com/Tomagoooo/status/1977251676471107989"},
    {"author":"Umie_0909","tweetId":"1961464595316617723","url":"https://x.com/Umie_0909/status/1961464595316617723"},
    {"author":"baiyuBYY","tweetId":"1964640119119659322","url":"https://x.com/baiyuBYY/status/1964640119119659322"},
    {"author":"22694BZ","tweetId":"1969303034892038223","url":"https://x.com/22694BZ/status/1969303034892038223"},
    {"author":"Saffron114214","tweetId":"1960324878688805286","url":"https://x.com/Saffron114214/status/1960324878688805286"},
    {"author":"NyakiJi","tweetId":"1961316512649658717","url":"https://x.com/NyakiJi/status/1961316512649658717"},
    {"author":"Saffron114214","tweetId":"1970070957579698340","url":"https://x.com/Saffron114214/status/1970070957579698340"},
    {"author":"bucishiro","tweetId":"1965840993250586869","url":"https://x.com/bucishiro/status/1965840993250586869"},
    {"author":"Saffron114214","tweetId":"1961694342982373811","url":"https://x.com/Saffron114214/status/1961694342982373811"},
    {"author":"NE2OP_","tweetId":"2006979231226708310","url":"https://x.com/NE2OP_/status/2006979231226708310"},
    {"author":"KimOcean7","tweetId":"1925222681605214605","url":"https://x.com/KimOcean7/status/1925222681605214605"},
    {"author":"Dekamimi_1917","tweetId":"1901905698667036832","url":"https://x.com/Dekamimi_1917/status/1901905698667036832"},
    {"author":"NE2OP_","tweetId":"2009229989238198624","url":"https://x.com/NE2OP_/status/2009229989238198624"},
    {"author":"NE2OP_","tweetId":"1991014012398809535","url":"https://x.com/NE2OP_/status/1991014012398809535"},
    {"author":"Umie_0909","tweetId":"2011778833045995808","url":"https://x.com/Umie_0909/status/2011778833045995808"},
    {"author":"Saffron114214","tweetId":"1979879346224660677","url":"https://x.com/Saffron114214/status/1979879346224660677"},
    {"author":"kurosawasan1202","tweetId":"2013284869087105120","url":"https://x.com/kurosawasan1202/status/2013284869087105120"},
    {"author":"Tomagoooo","tweetId":"1929275315454406973","url":"https://x.com/Tomagoooo/status/1929275315454406973"},
    {"author":"hiy09917190","tweetId":"1954448451300696143","url":"https://x.com/hiy09917190/status/1954448451300696143"},
    {"author":"22694BZ","tweetId":"1962167764669587768","url":"https://x.com/22694BZ/status/1962167764669587768"},
    {"author":"Saffron114214","tweetId":"2004149761319096821","url":"https://x.com/Saffron114214/status/2004149761319096821"},
    {"author":"shenwanjia_","tweetId":"2007047435760402538","url":"https://x.com/shenwanjia_/status/2007047435760402538"},
    {"author":"Saffron114214","tweetId":"1965724455638086066","url":"https://x.com/Saffron114214/status/1965724455638086066"},
    {"author":"kurosawasan1202","tweetId":"1982514280588312886","url":"https://x.com/kurosawasan1202/status/1982514280588312886"},
    {"author":"FiLha_Lindeza","tweetId":"1994706034905288781","url":"https://x.com/FiLha_Lindeza/status/1994706034905288781"},
    {"author":"Nhymoo","tweetId":"1935811901294100486","url":"https://x.com/Nhymoo/status/1935811901294100486"},
    {"author":"bucishiro","tweetId":"1987602800155717684","url":"https://x.com/bucishiro/status/1987602800155717684"},
    {"author":"Ainamachi","tweetId":"1990343761285816677","url":"https://x.com/Ainamachi/status/1990343761285816677"},
    {"author":"kurosawasan1202","tweetId":"1987224977624736098","url":"https://x.com/kurosawasan1202/status/1987224977624736098"},
    {"author":"llumine15","tweetId":"2009907416037765302","url":"https://x.com/llumine15/status/2009907416037765302"},
    {"author":"Saffron114214","tweetId":"1984506833365844143","url":"https://x.com/Saffron114214/status/1984506833365844143"},
    {"author":"FiLha_Lindeza","tweetId":"1991816357282037928","url":"https://x.com/FiLha_Lindeza/status/1991816357282037928"},
    {"author":"bucishiro","tweetId":"2009601019702075445","url":"https://x.com/bucishiro/status/2009601019702075445"},
    {"author":"NE2OP_","tweetId":"2013499889855144324","url":"https://x.com/NE2OP_/status/2013499889855144324"},
    {"author":"bucishiro","tweetId":"1978534997511356649","url":"https://x.com/bucishiro/status/1978534997511356649"},
    {"author":"coloring_k","tweetId":"2014850641110389015","url":"https://x.com/coloring_k/status/2014850641110389015"},
    {"author":"NobrainM27137","tweetId":"2013936934662410449","url":"https://x.com/NobrainM27137/status/2013936934662410449"},
]

if __name__ == "__main__":
    print(f"准备提交 {len(TWEETS)} 条推文...")
    
    success = 0
    for tweet in TWEETS:
        if submit_tweet(tweet):
            success += 1
            print(f"[Twitter] + @{tweet['author']}")
        else:
            print(f"[Twitter] x @{tweet['author']}")
        time.sleep(0.1)
    
    print(f"\n完成！成功提交 {success}/{len(TWEETS)} 条")
