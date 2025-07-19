from flask import Flask, render_template, jsonify, request, abort, Response
import os
import json
import requests
from game import game_bp
from 動物圖片 import gallery_bp
from cache import cache, save_cache_to_file

app = Flask(__name__)

app.register_blueprint(game_bp)
app.register_blueprint(gallery_bp)

CACHE_FILE_PATH = 'cache.json'
GITHUB_CACHE_URL = 'https://raw.githubusercontent.com/oounjh/Infopaw/main/cache.json'

# 啟動時載入本地快取
if os.path.exists(CACHE_FILE_PATH):
    with open(CACHE_FILE_PATH, 'r', encoding='utf-8') as f:
        app.cache = json.load(f)
else:
    app.cache = {}

# Render 啟動時抓最新 GitHub 快取
try:
    print('[INFO] 正在同步 GitHub 快取...')
    response = requests.get(GITHUB_CACHE_URL, timeout=10)
    if response.status_code == 200:
        app.cache = response.json()
        save_cache_to_file(app.cache)
        print('[INFO] GitHub 快取同步成功')
        print(f'[INFO] 快取中有多少平台資料：{len(app.cache)}')
    else:
        print(f'[WARN] GitHub 快取同步失敗，HTTP 狀態碼：{response.status_code}')
except Exception as e:
    print(f'[ERROR] GitHub 快取同步時發生錯誤：{e}')


API_KEY = os.getenv('API_KEY') or 'poko08564777'

@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/api/get_cache')
def api_get_cache():
    platform = request.args.get('platform')
    
    if not platform:
        return jsonify({'error': '缺少 platform 參數'}), 400
    cache = app.cache
    print(f'[DEBUG] 請求平台: {platform}')
    print(f'[DEBUG] 現有快取平台: {list(app.cache.keys())}')

    if platform == 'steam':
        steam_discount_games = cache.get('steam_discount', {}).get('data', [])
        steam_free_games = cache.get('steam_free', {}).get('data', [])
        games = steam_discount_games + steam_free_games
    elif platform == 'epic':
        games = cache.get('epic_free', {}).get('data', [])
    elif platform == 'gog':
        games = cache.get('gog_discount', {}).get('data', [])
    else:
        return jsonify({'error': '無效的平台'}), 400

    print(f'[DEBUG] 抓到遊戲數量：{len(games)}')
    return jsonify(games)

    
@app.route('/upload_cache', methods=['POST'])
def upload_cache():
    key = request.args.get('key')
    api_key = request.headers.get('X-API-KEY')
    data = request.get_json()

    if api_key != API_KEY:
        abort(403, description='API Key 不正確')

    if not key or not data:
        return jsonify({'error': '缺少key或資料'}),400
    
    try:
        app.cache[key] = data
        save_cache_to_file(app.cache)
        return jsonify({'message': f'{key}快取更新成功'})
    except Exception as e:
        return jsonify({'error': f'快取更新失敗: {e}'}),500


@app.route('/robots.txt')
def robots_txt():
    content = """User-agent: *
Allow: /
Sitemap: https://infopaw.onrender.com/sitemap.xml
"""
    return Response(content, mimetype='text/plain')

# 新增 sitemap.xml 路由
@app.route('/sitemap.xml')
def sitemap_xml():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://infopaw.onrender.com/</loc></url>
    <url><loc>https://infopaw.onrender.com/gallery</loc></url>
    <url><loc>https://infopaw.onrender.com/freegames</loc></url>
</urlset>
"""
    return Response(content, mimetype='application/xml')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, port=port, use_reloader=False)
