from flask import Flask, render_template, jsonify, request
import os
import requests
from game import game_bp
from 動物圖片 import gallery_bp

app = Flask(__name__)

app.register_blueprint(game_bp)
app.register_blueprint(gallery_bp)

LEAPCELL_API_URL = os.getenv('LEAPCELL_API_URL')
LEAPCELL_API_KEY = os.getenv('LEAPCELL_API_KEY')

HEADERS = {
    'Authorization': f'Bearer {LEAPCELL_API_KEY}'
}

@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/api/get_cache')
def get_cache():
    platform = request.args.get('platform')
    if not platform:
        return jsonify({'error': '缺少 platform 參數'}), 400
    try:
        url = f"{LEAPCELL_API_URL}/api/get_cache?platform={platform}"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        print(f"取得快取失敗: {e}")
        return jsonify({'error': '取得快取資料失敗'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, port=port, use_reloader=False)
