from flask import Blueprint, render_template, request, current_app
from cache import cache

game_bp = Blueprint('game',__name__, url_prefix='/freegames')

@game_bp.route('/')
def free_games_page():
    selected_platform = request.args.get('platform', '')
    selected_discount = request.args.get('discount_range', '') 
    search = request.args.get('search', '')


    #全部平台整合

    all_games = []
    for key in ['steam_discount', 'steam_free', 'epic_free', 'gog_discount']:
        all_games.extend(cache.get(key, []))
    
    filtered_games = all_games

    if selected_platform:
        filtered_games = [g for g in filtered_games if g['platform'] == selected_platform]

    if selected_discount and (selected_platform == '' or selected_platform == 'steam' or selected_platform == 'gog'):
        if selected_discount == '100':
            filtered_games = [g for g in filtered_games if g['discount_pct_value'] == 100]
        elif selected_discount == '80-99':
            filtered_games = [g for g in filtered_games if 80 <= g['discount_pct_value'] <= 99]
        elif selected_discount == '60-79':
            filtered_games = [g for g in filtered_games if 60 <= g['discount_pct_value'] <= 79]
        elif selected_discount == '40-59':
            filtered_games = [g for g in filtered_games if 40 <= g['discount_pct_value'] <= 59]
        elif selected_discount == '20-39':
            filtered_games = [g for g in filtered_games if 20 <= g['discount_pct_value'] <= 39]
        elif selected_discount == '1-19':
            filtered_games = [g for g in filtered_games if 1 <= g['discount_pct_value'] <= 19]

    if search:
        keyword = search.lower()
        filtered_games = [g for g in filtered_games if keyword in g['title'].lower()]

    print(f'[DEBUG] 抓到遊戲數量：{len(filtered_games)}')

    
    print(f'[DEBUG] 抓到遊戲數量：{len(filtered_games)}')
    return render_template('遊戲折扣通知.html',
                           games = filtered_games,
                           selected_platform = selected_platform,
                           selected_discount = selected_discount,
                           search = search)