import pickle
import streamlit as st
import requests

# OMDb API details
OMDB_API_KEY = 'b1031d63'
OMDB_API_URL = "http://www.omdbapi.com/?apikey={}&t={}"


# Function to fetch movie details from OMDb
def fetch_movie_details(movie_title):
    url = OMDB_API_URL.format(OMDB_API_KEY, movie_title)
    data = requests.get(url).json()
    if data['Response'] == 'True':
        return {
            "poster": data.get('Poster', "https://via.placeholder.com/300x450"),
            "title": data.get('Title', "N/A"),
            "genre": data.get('Genre', "N/A"),
            "actors": data.get('Actors', "N/A"),
            "plot": data.get('Plot', "N/A"),
            "imdbID": data.get('imdbID', None),  # Include IMDb ID for trailer search
            "rating": data.get('imdbRating', "N/A")  # Adding IMDb Rating
        }
    else:
        return {
            "poster": "https://via.placeholder.com/300x450",
            "title": "N/A",
            "genre": "N/A",
            "actors": "N/A",
            "plot": "N/A",
            "imdbID": None,
            "rating": "N/A"
        }


# Recommendation function
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []

    for i in distances[1:16]:
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(fetch_movie_details(movie_title))

    return recommended_movies


# Function to create social sharing links
def generate_social_links(title, imdbID):
    base_url = f"https://www.imdb.com/title/{imdbID}" if imdbID else ""
    twitter_url = f"https://twitter.com/intent/tweet?text=Check out {title}! {base_url}"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={base_url}"
    return twitter_url, facebook_url


# Streamlit app setup
st.set_page_config(page_title="Movie Recommender System", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Popular Movies", "Movie Recommendations", "Compare Movies"])

# Load preprocessed data
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values

# Add a predefined list of popular movies
popular_movies = [
    "The Shawshank Redemption",
    "The Godfather",
    "The Dark Knight",
    "Pulp Fiction",
    "Forrest Gump",
    "Inception",
    "Fight Club",
    "The Matrix",
    "The Lord of the Rings: The Return of the King",
    "Interstellar"
]

# CSS for custom button styles
st.markdown("""
    <style>
    .stButton {
        display: inline-block;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: bold;
        color: white;
        /* background-color: #007bff; */
        border-radius: 10px;
        text-decoration: none;
        margin: 5px;
        transition: all 0.3s ease;
    }
    .stButton:hover {
        transform: scale(1.05);
     /*   background-color: #0056b3; */
    }
    .trailer-button {
        /* background-color: #FF0000; */
    }
    .trailer-button:hover {
        background-color: #E60000;
    }
    .twitter-button {
       /* background-color: #1DA1F2; */
    }
    .twitter-button:hover {
        background-color: #0d8fe8;
    }
    .facebook-button {
       /* background-color: #1877F2; */
    }
    .facebook-button:hover {
        background-color: #165bd7;
    }
    </style>
""", unsafe_allow_html=True)

# Popular Movies Section
if selection == "Popular Movies":
    st.markdown("<h2 style='text-align: center; color: white;'>Popular Movies</h2>", unsafe_allow_html=True)
    popular_cols = st.columns(2)
    for idx, movie_title in enumerate(popular_movies):
        col = popular_cols[idx % len(popular_cols)]
        with col:
            details = fetch_movie_details(movie_title)
            twitter_url, facebook_url = generate_social_links(details['title'], details['imdbID'])
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{details['poster']}" alt="{details['title']} Poster">
                    <h3>{details['title']}</h3>
                    <p><strong>Genre:</strong> {details['genre']}</p>
                    <p><strong>Cast:</strong> {details['actors']}</p>
                    <p><strong>Plot:</strong> {details['plot']}</p>
                    <p><strong>IMDb Rating:</strong> {details['rating']}</p>
                    <a href="https://www.youtube.com/results?search_query={details['title']}+trailer" target="_blank" class="stButton trailer-button">
                        🎥 Watch Trailer
                    </a>
                    <a href="{twitter_url}" target="_blank" class="stButton twitter-button">
                        🐦 Share on Twitter
                    </a>
                    <a href="{facebook_url}" target="_blank" class="stButton facebook-button">
                        📘 Share on Facebook
                    </a>
                </div>
            """, unsafe_allow_html=True)

# Movie Recommendations Section
elif selection == "Movie Recommendations":
    st.markdown("<h2 style='text-align: center;'>Movie Recommendations</h2>", unsafe_allow_html=True)
    selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)
    if st.button('Show Recommendation'):
        recommendations = recommend(selected_movie)
        cols = st.columns(3)
        for idx, movie in enumerate(recommendations):
            col = cols[idx % 3]
            with col:
                twitter_url, facebook_url = generate_social_links(movie['title'], movie['imdbID'])
                trailer_url = f"https://www.youtube.com/results?search_query={movie['title']}+trailer"
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{movie['poster']}" alt="{movie['title']} Poster">
                        <h3>{movie['title']}</h3>
                        <p><strong>Genre:</strong> {movie['genre']}</p>
                        <p><strong>Cast:</strong> {movie['actors']}</p>
                        <p><strong>Plot:</strong> {movie['plot']}</p>
                        <p><strong>IMDb Rating:</strong> {movie['rating']}</p>
                        <a href="{trailer_url}" target="_blank" class="stButton trailer-button">
                            🎥 Watch Trailer
                        </a>
                        <a href="{twitter_url}" target="_blank" class="stButton twitter-button">
                            🐦 Share on Twitter
                        </a>
                        <a href="{facebook_url}" target="_blank" class="stButton facebook-button">
                            📘 Share on Facebook
                        </a>
                    </div>
                """, unsafe_allow_html=True)

# Movie Comparison Section
elif selection == "Compare Movies":
    st.markdown("<h2 style='text-align: center;'>Compare Movies</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        movie1 = st.selectbox("Select the first movie", movie_list)
    with col2:
        movie2 = st.selectbox("Select the second movie", movie_list)
    if st.button("Compare Movies"):
        movie1_details = fetch_movie_details(movie1)
        movie2_details = fetch_movie_details(movie2)
        st.write(f"### {movie1_details['title']} vs {movie2_details['title']}")

        # Display comparison details
        col1, col2 = st.columns(2)
        with col1:
            twitter_url, facebook_url = generate_social_links(movie1_details['title'], movie1_details['imdbID'])
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{movie1_details['poster']}" alt="{movie1_details['title']} Poster">
                    <h3>{movie1_details['title']}</h3>
                    <p><strong>Genre:</strong> {movie1_details['genre']}</p>
                    <p><strong>Cast:</strong> {movie1_details['actors']}</p>
                    <p><strong>Plot:</strong> {movie1_details['plot']}</p>
                    <p><strong>IMDb Rating:</strong> {movie1_details['rating']}</p>
                    <a href="{twitter_url}" target="_blank" class="stButton twitter-button">
                        🐦 Share on Twitter
                    </a>
                    <a href="{facebook_url}" target="_blank" class="stButton facebook-button">
                        📘 Share on Facebook
                    </a>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            twitter_url, facebook_url = generate_social_links(movie2_details['title'], movie2_details['imdbID'])
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{movie2_details['poster']}" alt="{movie2_details['title']} Poster">
                    <h3>{movie2_details['title']}</h3>
                    <p><strong>Genre:</strong> {movie2_details['genre']}</p>
                    <p><strong>Cast:</strong> {movie2_details['actors']}</p>
                    <p><strong>Plot:</strong> {movie2_details['plot']}</p>
                    <p><strong>IMDb Rating:</strong> {movie2_details['rating']}</p>
                    <a href="{twitter_url}" target="_blank" class="stButton twitter-button">
                        🐦 Share on Twitter
                    </a>
                    <a href="{facebook_url}" target="_blank" class="stButton facebook-button">
                        📘 Share on Facebook
                    </a>
                </div>
            """, unsafe_allow_html=True)
