from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from game import game_bp
from 動物圖片 import gallery_bp
from 免費遊戲通知.game_scraper import (
    get_steam_free_games, get_steam_free_permanent_games, 
    get_epic_free_games, get_gog_discount_games,
    save_cache)
import os


app = Flask(__name__)

app.register_blueprint(game_bp)
app.register_blueprint(gallery_bp)


@app.route('/')
def main_page():
    return render_template('main.html')


def auto_update_cache():
    print("[自動更新] 開始更新 Steam 特價...")
    steam_discount = get_steam_free_games()
    if steam_discount:
        save_cache('steam_discount', steam_discount)
        print(f"[自動更新] Steam 特價更新 {len(steam_discount)} 筆資料")

    print("[自動更新] 開始更新 Steam 限免...")
    steam_free = get_steam_free_permanent_games()
    if steam_free:
        save_cache('steam_free', steam_free)
        print(f"[自動更新] Steam 限免更新 {len(steam_free)} 筆資料")

    print("[自動更新] 開始更新 Epic 限免...")
    epic_free = get_epic_free_games()
    if epic_free:
        save_cache('epic_free', epic_free)
        print(f"[自動更新] Epic 限免更新 {len(epic_free)} 筆資料")

    print("[自動更新] 開始更新 GOG 特價...")
    gog_discount = get_gog_discount_games()
    if gog_discount:
        save_cache('gog_discount', gog_discount)
        print(f"[自動更新] GOG 特價更新 {len(gog_discount)} 筆資料")

    print("[自動更新] 所有平台更新完成")


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler(timezone=timezone('Asia/Taipei'))
        scheduler.add_job(auto_update_cache,'cron',hour=2,minute=0)
        scheduler.start()

        print("[排程] 已啟動自動更新任務，每天 2:00 會執行")

    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True)
    