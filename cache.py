import json

CACHE_FILE_PATH = 'cache.json'

cache = {}

def save_cache_to_file(data):
    with open(CACHE_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
