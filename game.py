from flask import Blueprint, render_template, request
from 免費遊戲通知.game_scraper import get_free_games

game_bp = Blueprint('game',__name__, url_prefix='/freegames')

@game_bp.route('/')
def free_games_page():
    selected_platform = request.args.get('platform', '')
    selected_discount = request.args.get('discount_range', '') 
    search = request.args.get('search', '')

    games = get_free_games(selected_platform, selected_discount, search)
    print(f'[DEBUG] 抓到遊戲數量：{len(games)}')
    return render_template('遊戲折扣通知.html',
                           games = games,
                           selected_platform = selected_platform,
                           selected_discount = selected_discount,
                           search = search)