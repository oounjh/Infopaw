import os
import requests
from cache import cache
import datetime
from 免費遊戲通知.game_scraper import (
    get_steam_free_games, get_steam_free_permanent_games,
    get_epic_free_games, get_gog_discount_games,
)

UPLOAD_URL = os.getenv('UPLOAD_URL') or 'https://infopaw.leapcell.app/upload_cache'

def upload_to_server(key, data):
    headers = {'X-API-KEY': 'poko08564777'}
    try:
        res = requests.post(f'{UPLOAD_URL}?key={key}', json=data, headers=headers)
        if res.status_code == 200:
            print(f'[UPLOAD] {key} 上傳成功')
        else:
            print(f'[UPLOAD] {key} 上傳失敗: {res.status_code}, {res.text}')
    except Exception as e:
        print(f'[UPLOAD] {key} 上傳失敗: {e}')


def update_all_and_upload(local=False):
    tasks = {
        'steam_discount': get_steam_free_games,
        'steam_free': get_steam_free_permanent_games,
        'epic_free': get_epic_free_games,
        'gog_discount': get_gog_discount_games
    }

    for key, func in tasks.items():
        print(f'[更新] 正在抓取 {key}')
        data = func()

        wrapped_data = {
            "last_updated": datetime.datetime.utcnow().isoformat(),
            "data": data
        }

        if local:
            cache[key] = wrapped_data
            print(f'[LOCAL] {key} 已載入快取')
        else:
            # GitHub Actions 模式，上傳到伺服器
            upload_to_server(key, wrapped_data)