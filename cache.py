
# import json
# import os

# CACHE_FILE = "cache.json"

# def _load_cache():
#     """Load the cache file or initialize an empty cache."""
#     if os.path.exists(CACHE_FILE):
#         try:
#             with open(CACHE_FILE, "r") as f:
#                 return json.load(f)
#         except json.JSONDecodeError:
#             print("Cache file is corrupted or empty. Resetting cache.")
#             return {}
#     return {}

# def _save_cache(cache):
#     """Save the cache dictionary to the file."""
#     with open(CACHE_FILE, "w") as f:
#         json.dump(cache, f, indent=4)
#     print("Cache updated successfully.")

# def get_cached_data(key):
#     """
#     Retrieve cached data for a specific key.
    
#     Args:
#         key (str): The key to look up in the cache.

#     Returns:
#         dict or None: The cached data or None if the key does not exist.
#     """
#     cache = _load_cache()
#     return cache.get(key)

# def cache_data(key, data):
#     """
#     Cache data under a specific key.

#     Args:
#         key (str): The key under which to store the data.
#         data (any): The data to be cached.
#     """
#     cache = _load_cache()
#     cache[key] = data
#     _save_cache(cache)

# def clear_cache():
#     """Clear the cache file by resetting it to an empty JSON object."""
#     _save_cache({})
#     print("Cache cleared.")
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

def get_cached_data(key):
    cache = _load_cache()
    return cache.get(key)

def cache_data(key, data):
    cache = _load_cache()
    cache[key] = data
    print(f"Caching data under key: {key}")  # Debugging
    _save_cache(cache)

def clear_cache():
    _save_cache({})
    print("Cache cleared.")
