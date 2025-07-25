import cloudscraper
import datetime
import time
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


#steam特惠
def get_steam_free_games(max_pages=5):
    base_url = "https://store.steampowered.com/search/?filter=onsale&specials=1&page={}"
    scraper = cloudscraper.create_scraper()

    games = []
    seen_likes = set()

    for page_num in range(1,max_pages + 1):
        url = base_url.format(page_num)
        print(f"[DEBUG] 正在抓取 Steam 特價第 {page_num} 頁")

        try:
            res = scraper.get(url)
            res.raise_for_status()
        except Exception as e:
            print(f"請求 Steam 網頁失敗：{e}")
            break

        soup = BeautifulSoup(res.text, 'html.parser')
        results = soup.select('.search_result_row')

        if not results:
            print(f"[INFO] 第 {page_num} 頁沒有資料，停止抓取")
            break


        for item in results:
            link = item['href'].split('?')[0]
            if link in seen_likes:
                continue

            seen_likes.add(link)

            title_tag = item.select_one('.title')
            title = title_tag.text.strip() if title_tag else '未知名稱'

            image_tag = item.select_one('img')
            image_small = ''
            image_big = ''

            if image_tag:
                image_small = image_tag.get('src') or image_tag.get('data-src') or ''
                image_big = re.sub(r'capsule_[^\/\?]*\.jpg', 'capsule_616x353.jpg', image_small)
            

            discount_block = item.select_one('.discount_block.search_discount_block')
            '''特價'''
            discount_pct = discount_block.select_one('.discount_pct') if discount_block else None
            '''原價'''
            original_price_div = discount_block.select_one('.discount_original_price') if discount_block else None
            '''現價'''
            final_price_div = discount_block.select_one('.discount_final_price') if discount_block else None

            discount = discount_pct.text.strip() if discount_pct else ''
            original_price = original_price_div.text.strip() if original_price_div else ''
            final_price = final_price_div.text.strip() if final_price_div else ''


            discount_pct_value = 0
            if discount:
                match = re.search(r'-(\d+)%', discount)
                if match:
                    discount_pct_value = int(match.group(1))


            games.append({
                'title': title,
                'image_small': image_small,
                'image_big' : image_big,
                'platform': 'steam',
                'link': link,
                'discount': discount,
                'original_price': original_price,
                'final_price': final_price,
                'discount_pct_value' : discount_pct_value,
                'type' : 'discount'
            })

        time.sleep(1)

    return games


#steam限免
def get_steam_free_permanent_games():
    url = "https://store.steampowered.com/search/?specials=1&maxprice=free"
    scraper = cloudscraper.create_scraper()


    try:
        res = scraper.get(url)
        res.raise_for_status()
    except Exception as e:
        print(f"請求 Steam 限免頁面失敗: {e}")
        return[]
    

    soup = BeautifulSoup(res.text, 'html.parser')
    games = []
    results = soup.select('.search_result_row')


    for item in results:
        title_tag = item.select_one('.title')
        title = title_tag.text.strip() if title_tag else '未知名稱'

        image_tag = item.select_one('img')
        image_small = ''
        image_big = ''

        if image_tag: 
            image_small = image_tag.get('src') or image_tag.get('data-src') or ''
            image_big = re.sub(r'capsule_[^\/\?]*\.jpg', 'capsule_616x353.jpg', image_small)
        
        link = item['href'].split('?')[0]



        games.append({
            'title': title,
            'image_small': image_small,
            'image_big': image_big,
            'platform': 'steam',
            'link': link,
            'discount' : '-100%',
            'original_price' : '未知',
            'final_price' : '免費',
            'discount_pct_value' : 100,
            'type' : 'free'
        })


    return games


#Epic網頁請求
def get_epic_games_raw():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=zh-Hant&country=TW&allowCountries=TW"
    scraper = cloudscraper.create_scraper()


    try:
        res = scraper.get(url)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"請求 Epic 網頁失敗: {e}")
        return None
    
#Epic特價
def parse_epic_game(element, is_free=False):
    title = element.get('title', '未知名稱')
    product_slug = element.get('productSlug') or ''
    
    if not product_slug:
        mappings = element.get('catalogNs', {}).get('mappings')
        if mappings and len(mappings) > 0:
            product_slug = mappings[0].get('pageSlug')
    

    if not product_slug:
        return None
    

    image_small = ''
    image_big = ''
    for img in element.get('keyImages', []):
        if img.get('type') == 'DieselStoreFrontWide':
            image_big = img.get('url')
        if img.get('type') == 'Thumbnail':
            image_small = img.get('url')


    link = f"https://store.epicgames.com/p/{product_slug}"


    original_price = '未知'
    final_price = '免費' if is_free else '未知'
    discount_pct_value = 100 if is_free else 0
    discount = '-100%' if is_free else ''

    return{
        'title': title,
        'image_small': image_small,
        'image_big': image_big or image_small,
        'platform': 'epic',
        'link': link,
        'discount' : discount,
        'original_price' : original_price,
        'final_price' : final_price,
        'discount_pct_value' : discount_pct_value,
        'type' : 'free' if is_free else 'discount'

    }
            
        
#Epic限免
def get_epic_free_games():
    data = get_epic_games_raw()
    if not data:
        return []
    

    games = []
    now = datetime.datetime.utcnow().isoformat()


    for element in data['data']['Catalog']['searchStore']['elements']:
        promotions = element.get('promotions') or {}
        current_offers = promotions.get('promotionalOffers', [])
        upcoming_offers = promotions.get('upcomingPromotionalOffers',[])


        def is_active(offers):
            for promo in offers:
                for offer in promo.get('promotionalOffers', []):
                    start = offer.get('startDate')
                    end = offer.get('endDate')
                    if start <= now <=end:
                        return True
            return False
        
        def is_upcoming(offers):
            for promo in offers:
                for offer in promo.get('promotionalOffers', []):
                    start = offer.get('startDate')
                    if now < start: 
                        return True
            return False
        
        if is_active(current_offers):
            game = parse_epic_game(element, is_free=True)
            if game:
                games.append(game)

        elif is_upcoming(upcoming_offers):
            game = parse_epic_game(element, is_free=True)
            if game:
                game['type'] = 'upcoming'
                games.append(game)

    return games
            
'''
        if not promotions:
            continue

        
        for promo in promotions.get('promotionalOffers', []):
            for offer in promo.get('promotionalOffers', []):
                try:
                    start = offer.get('startDate')
                    end = offer.get('endDate')
                    if start <= now <= end:
                        game = parse_epic_game(element, is_free=True)
                        if game:
                            games.append(game)
                        break
                except Exception as e:
                    print(f"解析 Epic 遊戲時間時發生錯誤: {e}")
            else:
                continue
            break


    return games
'''


#gog
def get_gog_discount_games():
    url = "https://www.gog.com/games?price=discounted&sort=popularity&page=1"
    games = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, timeout=25000, wait_until='load')
            page.wait_for_selector('.product-tile img', timeout=25000)
            page.wait_for_timeout(6000)
            content = page.content()
        except Exception as e:
            print(f"[ERROR] 請求 GOG 網頁失敗: {e}")
            return []
        finally:
            browser.close()

        soup = BeautifulSoup(content, 'html.parser')

        game_cards = soup.select('a.product-tile')

        for card in game_cards:
            title_tag = card.select_one('product-title span')
            title = title_tag.text.strip() if title_tag else '未知名稱'


            image_url = ''
            picture_tag = card.select_one('picture')
            if picture_tag:
                source_jpng = picture_tag.select_one('source[type="image/jpeg"]')
                if source_jpng and source_jpng.has_attr('srcset'):
                    image_url = source_jpng['srcset'].split(',')[0].strip()
                else:
                    img_tag = picture_tag.select_one('img')
                    if img_tag and img_tag.has_attr('src'):
                        image_url = img_tag['src']
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url.startswith('/'):
                    image_url = 'https://www.gog.com' + image_url
            else:
                img_tag = card.select_one('img')
                if img_tag and img_tag.has_attr('src'):
                    image_url = img_tag['src']

            
            href = card.get('href', '')
            link = f"https://www.gog.com{href}" if href.startswith('/') else href


            
            discount_tag = card.select_one('price-discount')
            discount = discount_tag.text.strip() if discount_tag else ''

            discount_pct_value = 0
            if discount:
                match = re.search(r'(\d+)%', discount)
                if match:
                    discount_pct_value = int(match.group(1))

            original_price_tag = card.select_one('.base-value')
            original_price = original_price_tag.text.strip() if original_price_tag else '未知'

            final_price_tag = card.select_one('.final-value')
            final_price = final_price_tag.text.strip() if final_price_tag else '免費'

            if discount_pct_value > 0:
                games.append({
                    'title': title,
                    'image_small': image_url,
                    'image_big': image_url,
                    'platform': 'gog',
                    'link': link,
                    'discount': f"-{discount_pct_value}%",
                    'original_price': original_price,
                    'final_price': final_price,
                    'discount_pct_value': discount_pct_value,
                    'type': 'discount'
                })

        browser.close()

    print(f"[DEBUG] GOG 爬到遊戲數量：{len(games)}")
    return games




#全

def get_cached_or_fetch(platform_key, fetch_function):
    print(f"[爬蟲] {platform_key} 重新抓取資料（API 快取邏輯外部處理）")
    data = fetch_function()
    return data if data else []

