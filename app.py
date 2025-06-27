from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from game import game_bp
from 動物圖片 import gallery_bp
from 免費遊戲通知.game_scraper import fetch_all_games, save_cache
import os


app = Flask(__name__)

app.register_blueprint(game_bp)
app.register_blueprint(gallery_bp)


@app.route('/')
def main_page():
    return render_template('main.html')


def auto_update_cache():
    print("[自動更新] 開始更新資料...")
    games = fetch_all_games()
    if games:
        save_cache(games)
        print(f"[自動更新] 完成，更新 {len(games)} 筆資料")
    else:
        print("[自動更新] 更新失敗，資料為空")


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler(timezone=timezone('Asia/Taipei'))
        scheduler.add_job(auto_update_cache,'cron',hour=2,minute=0)
        scheduler.start()

        print("[排程] 已啟動自動更新任務，每天 2:00 會執行")

    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True)
    