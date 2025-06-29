import os
import requests
from 免費遊戲通知.game_scraper import (
    get_steam_free_games, get_steam_free_permanent_games,
    get_epic_free_games, get_gog_discount_games,
)

LEAPCELL_API_URL = os.getenv('LEAPCELL_API_URL')
LEAPCELL_API_KEY = os.getenv('LEAPCELL_API_KEY')

HEADERS = {
    'Authorization': f'Bearer {LEAPCELL_API_KEY}',
    'Content-Type': 'application/json'
}

def upload_cache(platform, data):
    url = f"{LEAPCELL_API_URL}/upload_cache?key={platform}"
    response = requests.post(url, json=data, headers=HEADERS)
    
    if response.status_code == 200:
        print(f"[上傳成功] {platform} 快取已更新")
    else:
        print(f"[上傳失敗] {platform} 快取更新失敗: {response.status_code} {response.text}")

def main():
    steam_discount = get_steam_free_games()
    upload_cache('steam_discount', steam_discount)

    steam_free = get_steam_free_permanent_games()
    upload_cache('steam_free', steam_free)

    epic_free = get_epic_free_games()
    upload_cache('epic_free', epic_free)

    gog_discount = get_gog_discount_games()
    upload_cache('gog_discount', gog_discount)

if __name__ == '__main__':
    main()
