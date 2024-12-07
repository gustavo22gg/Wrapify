

#work
from flask import Flask, request, jsonify, redirect, url_for, render_template
from dotenv import load_dotenv
from cache import get_cached_data, cache_data, clear_cache, clear_user_cache

import os
import requests
import time
import cache
import json
import openai
# Load environment variables
load_dotenv()

client_id = os.getenv('clientid')
client_secret = os.getenv('clientSec')
redirect_uri = 'https://wrapify-ylor.onrender.com/callback'
openai.api_key = os.getenv('OPENAI_API_KEY')  # Ensure this is set in your .env file


# Flask app setup
app = Flask(__name__)
auth_code = None
access_token = None


def get_auth_url():
    scope = 'user-top-read user-read-recently-played user-read-playback-state'
    return f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"

@app.route('/')
def home():
    return render_template('index.html')  # Home page with login button

@app.route('/login')
def login():
    auth_url = get_auth_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')
    if auth_code:
        get_access_token()

        # Clear cache for the user
        user_id = get_user_profile().get('id')
        if user_id:
            clear_user_cache(user_id)

        return redirect(url_for('dashboard'))
    return "Authorization failed. Please try again."

def clear_user_cache(user_id):
    cache_data = cache._load_cache()  # Avoid using "cache" as a variable
    user_keys = [key for key in cache_data.keys() if key.startswith(f"{user_id}_")]
    for key in user_keys:
        del cache_data[key]
    cache._save_cache(cache_data)  # Save updated cache
    print(f"Cache cleared for user {user_id}")


def get_access_token():
    global access_token, token_expiry_time
    token_url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(token_url, data=data)
    token_info = response.json()
    access_token = token_info.get('access_token')
    expires_in = token_info.get('expires_in', 0)
    token_expiry_time = time.time() + expires_in

def is_token_valid():
    return access_token is not None and time.time() < token_expiry_time
@app.route('/logout', methods=['POST'])
def logout():
    global access_token, auth_code
    # Clear the session variables
    access_token = None
    auth_code = None
    # Redirect to the home page
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/dashboard')
def dashboard():
    if not is_token_valid():
        return redirect(url_for('login'))

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.spotify.com/v1/me/top/tracks?limit=10', headers=headers)

    genre_counts = {}
    if response.status_code == 200:
        for track_item in response.json().get('items', []):
            artist_id = track_item['artists'][0]['id']
            artist_info = get_artist_info(artist_id)
            genres = artist_info.get('genres', [])
            for genre in genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_10_genres = [genre for genre, _ in sorted_genres]
    top_10_counts = [10] * len(top_10_genres)

    # Fetch the user's profile
    user_profile = get_user_profile()
    username = user_profile.get('display_name', 'Guest')  # Fallback to "Guest"

    top_tracks()
    top_artists()
    playlists()
    listening_history()  # Add this to fetch and cache listening history

    with open('cache.json', 'r') as f:
        cache_data = json.load(f)

    return render_template(
        'dashboard.html',
        genres=top_10_genres,
        genre_counts=top_10_counts,
        cache_data=cache_data,
        username=username
    )


  


@app.route('/analyze_personality', methods=['GET'])
def analyze_personality():
    # Load cached data
    cached_data = cache.load_cached_analysis()
    cached_analysis = cached_data.get('personality_analysis')

    # Return cached analysis if it exists
    if cached_analysis:
        return jsonify({"personality_analysis": cached_analysis})

    # Generate new analysis
    with open('cache.json', 'r') as f:
        cache_data = json.load(f)

    genres = cache_data.get('top_genres', [])
    top_tracks = [track.get('name') for track in cache_data.get('top_tracks', [])]
    top_artists = [artist.get('name') for artist in cache_data.get('top_artists', [])]

    # Fetch the user's profile for username
    user_profile = get_user_profile()
    username = user_profile.get('display_name', 'Guest')
    messages = [
    {
        "role": "system",
        "content": """
        You are a close friend of the user, full of warmth and personality. Write in a casual, friendly tone, like you're chatting at a coffee shop. Forget about being formal or perfect—just share your thoughts naturally, with a sprinkle of humor and real emotion. Don't sound robotic; keep it fun and lighthearted!
        """
    },
    {
        "role": "user",
        "content": f"""
        Hey {username}! Okay, so here's the deal—I peeked at your music preferences, and wow, your playlist is something else! It's giving me *major vibes* about who you are as a person. Here's what you’re into:
        - Genres: {', '.join(genres)}
        - Top Songs: {', '.join(top_tracks)}
        - Top Artists: {', '.join(top_artists)}
        *****write under 300 word********!!

        Based on this, tell me who you think I am! Make it fun, like you're hyped to talk about me. Imagine we're just friends joking around, and you're describing me to someone else.
        """
    }
]


 

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=messages,
            max_tokens=400,
            temperature=0.7
        )
        analysis = response.choices[0].message['content'].strip()

        # Save analysis to cache
        cached_data['personality_analysis'] = analysis
        cache.save_cached_analysis(cached_data)

        return jsonify({"personality_analysis": analysis})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to analyze personality"}), 500

@app.route('/top_artists')
def top_artists():
    # Fetch the user's Spotify ID
    user_id = get_user_profile().get('id')  # Ensure user ID is fetched

    if not user_id:
        return jsonify({"error": "Failed to identify user"}), 400

    # Check if the data is already cached for this user
    cached_artists = get_cached_data(user_id, "top_artists")
    if cached_artists:
        print(f"Cache hit for user {user_id} - top artists")
        return jsonify(cached_artists)  # Return cached data

    print(f"Cache miss for user {user_id} - fetching top artists")
    # Fetch from Spotify API if not cached
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.spotify.com/v1/me/top/artists?limit=12', headers=headers)

    artist_data = []
    if response.status_code == 200:
        for artist_item in response.json().get('items', []):
            artist_data.append({
                'name': artist_item['name'],
                'genres': ', '.join(artist_item.get('genres', [])),
                'popularity': artist_item.get('popularity', 'N/A'),
                'url': artist_item['external_urls']['spotify']  # Add Spotify profile link
            })

        # Cache the data for this user
        cache_data(user_id, "top_artists", artist_data)
        return jsonify(artist_data)

    return jsonify({"error": "Failed to get top artists"})

def get_artist_info(artist_id):
    """Fetch artist details, including genres, for a given artist ID."""
    artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(artist_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get artist info for artist ID {artist_id}. Status code: {response.status_code}")
        return {}    


@app.route('/listening_history')
def listening_history():
    user_id = get_user_profile().get('id')
    if not user_id:
        return jsonify({"error": "Failed to identify user"}), 400

    cached_history = get_cached_data(user_id, "listening_history")
    if cached_history:
        return jsonify(cached_history)

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.spotify.com/v1/me/player/recently-played?limit=15', headers=headers)

    if response.status_code == 200:
        history_data = [
            {
                'name': item['track']['name'],
                'artist': ', '.join(artist['name'] for artist in item['track']['artists']),
                'album': item['track']['album']['name'],
                'played_at': item['played_at'],
                'url': item['track']['external_urls']['spotify']
            }
            for item in response.json().get('items', [])
        ]
        cache_data(user_id, "listening_history", history_data)
        return jsonify(history_data)

def get_track_features(track_id):

    features_url = f'https://api.spotify.com/v1/audio-features/{track_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(features_url, headers=headers)
    
    if response.status_code == 200:
        features = response.json()
        return {
            'danceability': features['danceability'],
            'energy': features['energy'],
            'key': features['key'],
            'loudness': features['loudness'],
            'tempo': features['tempo'],
            'valence': features['valence'],
            'popularity': features.get('popularity', 'N/A')  # popularity might not be available in this API
        }
    else:
        print(f"Failed to get features for track {track_id}. Status code: {response.status_code}")
        return {}

def get_user_profile():
    """Fetch the current user's profile information."""
    profile_url = 'https://api.spotify.com/v1/me'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(profile_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get user profile. Status code: {response.status_code}")
        return {}


@app.route('/top_tracks')
def top_tracks():
    user_id = get_user_profile().get('id')  # Fetch Spotify user ID
    if not user_id:
        return jsonify({"error": "Failed to identify user"}), 400

    # Retrieve cached data for this user
    cached_tracks = get_cached_data(user_id, "top_tracks")
    if cached_tracks:
        print(f"Cache hit for user {user_id}")
        return jsonify(cached_tracks)

    print(f"Cache miss for user {user_id}")
    # Fetch fresh data from Spotify
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.spotify.com/v1/me/top/tracks?limit=12', headers=headers)

    if response.status_code == 200:
        track_info = []
        for track_item in response.json().get('items', []):
            track_info.append({
                'name': track_item['name'],
                'artist': ', '.join(artist['name'] for artist in track_item['artists']),
                'popularity': track_item.get('popularity', 'N/A'),
                'url': track_item['external_urls']['spotify']
            })

        # Cache the data for the specific user
        cache_data(user_id, "top_tracks", track_info)
        return jsonify(track_info)

    return jsonify({"error": "Failed to fetch top tracks"})

@app.route('/playlists')
def playlists():
    user_id = get_user_profile().get('id')
    if not user_id:
        return jsonify({"error": "Failed to identify user"}), 400
    # Check if the data is already cached
    cached_playlists = cache.get_cached_data(user_id, "playlists")
    if cached_playlists:
        return jsonify(cached_playlists)  # Return cached data

    # Fetch from Spotify API
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)

    if response.status_code == 200:
        playlist_data = []
        for playlist in response.json().get('items', []):
            playlist_data.append({
                'name': playlist['name'],
                'url': playlist['external_urls']['spotify'],  # Add Spotify playlist link
                'tracks': playlist['tracks']['total']  # Total number of tracks (optional)
            })

        # Cache the data
        cache.cache_data(user_id, "playlists", playlist_data)
        return jsonify(playlist_data)

    return jsonify({"error": "Failed to get playlists"})

# if __name__ == '__main__':
#     app.run(port=8888)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
