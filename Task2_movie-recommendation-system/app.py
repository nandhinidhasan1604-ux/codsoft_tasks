from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import requests
import os

app = Flask(__name__)

# ── API Key ──
OMDB_API_KEY = 'fe48af21'

# ── Load data once when app starts ──
BASE = os.path.dirname(os.path.abspath(__file__))

df = pd.read_csv(os.path.join(BASE, 'ml-100k', 'u.data'), sep='\t',
                 names=['user_id', 'movie_id', 'rating', 'timestamp'])

movies = pd.read_csv(os.path.join(BASE, 'ml-100k', 'u.item'),
                     sep='|', encoding='latin-1',
                     usecols=[0, 1],
                     names=['movie_id', 'title'])

matrix = df.pivot_table(index='user_id', columns='movie_id', values='rating')
matrix = matrix.fillna(0)

user_similarity = cosine_similarity(matrix)
user_sim_df = pd.DataFrame(user_similarity,
                            index=matrix.index,
                            columns=matrix.index)

all_movie_ids = set(df['movie_id'].unique())

print("Ready!")

# ── Get movie poster from OMDb ──
def get_poster(movie_title):
    try:
        clean_title = movie_title.split('(')[0].strip()
        url = f"http://www.omdbapi.com/?t={clean_title}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        poster = data.get('Poster', '')
        if poster and poster != 'N/A':
            return poster
        # Nice placeholder with movie title
        encoded = clean_title.replace(' ', '+')
        return f"https://via.placeholder.com/80x115/1a1a22/a78bfa?text={encoded}"
    except:
        return "https://via.placeholder.com/80x115/1a1a22/a78bfa?text=Movie"

# ── Recommendation function ──
def recommend_movies(user_id, num=5):
    similar_users = user_sim_df[user_id].sort_values(ascending=False)
    similar_users = similar_users.drop(user_id)
    top_similar = similar_users.head(5).index.tolist()

    watched = set(df[df['user_id'] == user_id]['movie_id'].values)
    not_watched = list(all_movie_ids - watched)

    scores = {}
    for movie in not_watched:
        score = 0
        for sim_user in top_similar:
            score += matrix.loc[sim_user, movie] * user_sim_df.loc[user_id, sim_user]
        if score > 0:
            scores[movie] = score

    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:num]

    results = []
    for movie_id, score in top:
        row = movies[movies['movie_id'] == movie_id]
        if row.empty:
            continue
        title = row.iloc[0]['title']
        results.append({
            'title': title,
            'score': round(score, 2),
            'movie_id': int(movie_id),
            'poster': get_poster(title)
        })
    return results        # ← this was missing before

# ── Flask routes ──
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend')
def recommend():
    try:
        user_id = int(request.args.get('user_id'))
        if user_id < 1 or user_id > 943:
            return jsonify({'error': 'User ID must be between 1 and 943'}), 400
        results = recommend_movies(user_id)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)