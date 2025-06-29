from flask import Flask, render_template, jsonify, request
import os
from update_and_upload import upload_cache
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
app.cache = {}

@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/api/get_cache')
def get_cache():
    platform = request.args.get('platform')
    if not platform:
        return jsonify({'error': '缺少 platform 參數'}), 400
    if platform not in app.cache:
        return jsonify({'error': f'{platform} 的快取不存在'}), 404
    
    return jsonify(app.cache[platform])
    
@app.route('/upload_cache', methods=['POST'])
def upload_cache():
    key = request.args.get('key')
    data = request.get_json()

    if not key or not data:
        return jsonify({'error': '缺少key或資料'}),400
    
    try:
        app.cache[key] = data
        return jsonify({'message': f'{key}快取更新成功'})
    except Exception as e:
        return jsonify({'error': f'快取更新失敗: {e}'}),500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, port=port, use_reloader=False)
