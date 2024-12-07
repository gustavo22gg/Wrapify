
import json
import os

CACHE_FILE = "cache.json"
CACHEe_FILE = 'personality_cache.json'

def load_cached_analysis():
    if os.path.exists(CACHEe_FILE):
        with open(CACHEe_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cached_analysis(data):
    with open(CACHEe_FILE, 'w') as f:
        json.dump(data, f)

def _load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Cache file is corrupted or empty. Resetting cache.")
            return {}
    return {}

def _save_cache(cache):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=4)
        print("Cache saved successfully.")
    except Exception as e:
        print(f"Failed to save cache: {e}")

def get_cached_data(user_id, key):
    cache = _load_cache()
    user_specific_key = f"{user_id}_{key}"
    cached_entry = cache.get(user_specific_key)
    if cached_entry:
        # Check if the cache is expired
        if time.time() - cached_entry["timestamp"] > cached_entry["ttl"]:
            print(f"Cache expired for key: {user_specific_key}")
            return None
        return cached_entry["data"]
    return None


def cache_data(user_id, key, data, ttl=3600):
    cache = _load_cache()
    user_specific_key = f"{user_id}_{key}"
    cache[user_specific_key] = {
        "data": data,
        "timestamp": time.time(),
        "ttl": ttl
    }
    _save_cache(cache)



def clear_cache():
    _save_cache({})
    print("Cache cleared.")
