from flask import Blueprint, render_template,request
import requests
import random
from 自動化網站抓圖.animal_facts import animal_facts
from 自動化網站抓圖.photo_filter import get_exclude_keywords_for_category, filter_photos_by_keywords


gallery_bp = Blueprint('gallery',__name__)

API_KEY = "zJWYdamQugniIebxwRyGyWUKalFNbIcZuq0Hfsg6TG4zkGAjBLxO5ZbK"
headers = {'Authorization': API_KEY}


fallback_images = {
    'hamster': {
        'url':'/static/hamster.jpg',
        'photographer': '倉鼠',
        'photographer_url':'#',
        'photo_url':'#'
    }
}



def get_animal_photos(query,per_page=20):
    page = random.randint(1,20)
    url = f'https://api.pexels.com/v1/search?query={query}&per_page={per_page}&page={page}'
    response = requests.get(url,headers=headers)
    data = response.json()


    photos = []
    for photo in data.get('photos',[]):
        photos.append({
            'url': photo['src']['medium'], 
            'photographer': photo['photographer'],
            'photographer_url' : photo['photographer_url'],
            'photo_url' : photo['url'],
            'alt' : photo.get('alt', '') 
        })


    """"
    print("=== 檢查中 ===")
    for photo in photos:
        combined = ' '.join([
            photo.get('alt',''),
            photo.get('url',''),
            photo.get('photographer',''),
            photo.get('photographer_url','')
        ]).lower()
        print(combined)
    """


    return photos


#抓取圖片數
def get_photos_with_fallback(animal, per_page=20, exclude_keywords=None):
    photos = get_animal_photos(animal, per_page)
    filtered = filter_photos_by_keywords(photos,exclude_keywords)
    if filtered:
        return filtered
    elif animal in fallback_images:
        return [fallback_images[animal]]
    else:
        return []


photos = get_photos_with_fallback('hamster')
for p in photos:
        print(p['url'])



@gallery_bp.route('/gallery')
def gallery():
    category_groups = {
        '哺乳類':['dog','cat','hamster','rabbit','hedgehog','fox','elephant'],
        '鳥類':['bird','parrot','eagle','owl','penguin','flamingo','peacock','crow'],
        '爬蟲類':['lizard','snake','turtle','chameleon','gecko','pythons'],
        '水中動物':['fish','dolphin','whale','octopus','crab','starfish']
    }
   
    display_names = {'dog': '狗','cat': '貓','hamster': '倉鼠','rabbit': '兔子','fox': '狐狸','hedgehog':'刺蝟', 'elephant': '大象',
                    'bird': '鳥', 'parrot': '鸚鵡', 'eagle': '老鷹','owl':'貓頭鷹','penguin':'企鵝','flamingo':'紅鶴','peacock':'孔雀','crow':'烏鴉',
                    'lizard': '蜥蜴', 'snake': '蛇', 'turtle': '烏龜','chameleon': '變色龍','gecko': '壁虎','pythons': '巨蟒',
                    'fish': '魚', 'dolphin': '海豚', 'whale': '鯨魚','octopus': '章魚', 'crab': '螃蟹', 'starfish': '海星'
                     }
    

    selected = request.args.get('category',default=None)

    exclude_keywords = get_exclude_keywords_for_category(selected)

    selected_fact = None
    if selected and selected in animal_facts:
        fact_list = animal_facts[selected]
        selected_fact = random.choice(fact_list)

    
    gallery = {}
    if selected in display_names:
        gallery = {selected: get_photos_with_fallback(selected, exclude_keywords=exclude_keywords)}

    return render_template('動物圖片.html',
                           gallery=gallery,
                           category_groups=category_groups,
                           selected=selected,
                           display_names=display_names,
                           animal_facts=animal_facts if selected else {},
                           selected_fact=selected_fact
                           )