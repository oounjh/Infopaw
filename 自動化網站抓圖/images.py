import requests

API_KEY = "zJWYdamQugniIebxwRyGyWUKalFNbIcZuq0Hfsg6TG4zkGAjBLxO5ZbK"
headers = {'Authorization': API_KEY}

def get_animal_photos(query='dog',per_page='5'):
    url = f'https://api.pexels.com/v1/search?query={query}&per_page={per_page}'
    response = requests.get(url,headers=headers)
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