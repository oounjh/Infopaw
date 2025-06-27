import re
from .exclude_keywords import exclude_keywords_map


def get_exclude_keywords_for_category(category):
    return [kw.lower() for kw in exclude_keywords_map.get(category, [])]

manual_exclude_urls = [
    "https://www.pexels.com/photo/delicious-takoyaki-street-food-in-vietnam-31302952/",
    "https://www.pexels.com/photo/a-bowl-of-ramen-with-an-egg-and-meat-16068666/",
    "https://www.pexels.com/photo/a-bowl-of-ramen-with-meat-and-eggs-16068665/"

]

manual_exclude_photographers = [
     "COPPERTIST WU"
]

def normalize_text(text):
     return re.sub(r'[^\w\s]','',text.lower())

def contains_keyword(text, keywords):
    normalize = normalize_text(text)
    for kw in keywords:
        if kw in normalize:
            return True
    return False

def filter_photos_by_keywords(photos,exclude_keywords):
    if exclude_keywords is None:
        exclude_keywords = []

    filtered = []
    for photo in photos:
            url = photo.get('photo_url','').lower()
            if url in manual_exclude_urls:
                 print(f"已排除照片:{url}")
                 continue
            
            photographers = photo.get('photographer','').lower()
            if photographers in [p.lower() for p in manual_exclude_photographers]:
                 print(f"已排除攝影師:{photographers}")
                 continue
            


            text_to_check = ' '.join([
                photo.get('alt','') or '',
                photo.get('url','') or '',
                photo.get('photographer','') or '',
                photo.get('photographer_url','') or '',
                photo.get('photo_url','') or ''
            ]).lower()


            print(f"檢查照片URL: {photo.get('photo_url')}")
            print(f"合併文字: {text_to_check}")


            if contains_keyword(text_to_check, exclude_keywords):
                print(f"排除照片因為包含關鍵字: {exclude_keywords} => {text_to_check}")
                continue
            filtered.append(photo)
    return filtered
    