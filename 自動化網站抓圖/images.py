import requests
import os
from dotenv import load_dotenv

API_KEY = os.environ.get('PEXELS_API_KEY')

if not API_KEY:
    raise ValueError("未偵測到 PEXELS_API_KEY 環境變數，請檢查設定！")

headers = {'Authorization':API_KEY}

def get_animal_photos(query='dog',per_page='5'):
    url = f'https://api.pexels.com/v1/search?query={query}&per_page={per_page}'
    response = requests.get(url,headers=headers)

    if response.status_code !=200:
        return f"Error: {response.status_code}"

    data = response.json()
    photos = []
    for photo in data['photos']:
        photos.append({
            'url' : photo['src']['medium'],
            'photographer' : photo['photographer'],
            'id' : photo['id']
        })
    return photos

dog_photos = get_animal_photos('dog',10)
print(dog_photos)