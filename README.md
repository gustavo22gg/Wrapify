# Wrapify — Spotify Dashboard + AI Personality Analyzer

Wrapify is a Flask web app that connects to your Spotify account and visualizes your listening data (top tracks, top artists, playlists, and recent history). It also includes an **AI-powered personality analysis** of your music taste. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}

---

## 🚀 Features

- **Spotify Login & Session** — Secure login flow and logout. 
- **Interactive Dashboard**
  - Top Tracks / Top Artists
  - Playlists
  - Listening History (with timestamps)
  - **Top Genres Pie Chart** (Chart.js)
  - **AI Personality Analysis** button (calls `/analyze_personality`)  
  - Account menu with **Logout** action  
  *(All rendered via Jinja templates and client-side JS.)
- **Modern UI** — Responsive layout and custom styles.

---

## 🧰 Tech Stack

- **Backend:** Python, Flask, Jinja2 
- **Frontend:** HTML, CSS, Chart.js (CDN) 
- **AI:** OpenAI API for personality analysis 
Key Python packages (see `requirements.txt`): `Flask`, `gunicorn`, `openai`, `python-dotenv`, `requests` (or `httpx`).

---

## 📦 Project Structure

```
├─ app.py # Flask app (routes, auth, views)
├─ cache.py # Caching/utilities (used by dashboard data)
├─ requirements.txt
├─ README.md
├─ Procfile # For WSGI deployment (e.g., Gunicorn)
├─ templates/
│ ├─ index.html # Login page
│ └─ dashboard.html # Main dashboard (charts + sections)
└─ static/
└─ style.css # Stylesheet
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your_flask_secret_key

# Spotify OAuth
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:5000/callback

# OpenAI (for Personality Analysis)
OPENAI_API_KEY=your_openai_api_key
```
The dashboard expects server-provided data like genres and cache_data, and exposes endpoints such as /analyze_personality and /logout. 
