import streamlit as st
import pandas as pd
import math

# -----------------------------
# History & TODO
# -----------------------------
# 2026-01-31: Initial version
# 2026-02-01: Added random mode, mouse-over effects, IMDB links, rating filter

# TODO - remove blue underlines from links in custom CSS
# TODO - allow sort to change ascending/descending, sort after random mode
# TODO - make accessible from remote URL (Streamlit Cloud or similar)


# -----------------------------
# CONFIG
# -----------------------------
CSV_FILE = "movie_database.csv"

st.set_page_config(layout="wide")
st.title("🎬 Movie Database")

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
/* Anchor fills the column */
.movie-link {
    text-decoration: none;
    color: inherit;
    display: block;
    width: 100%;
}

/* Card styling */
.movie-card {
    width: 100%;
    box-sizing: border-box;  /* includes padding in width */
    background-color: #111;
    padding: 6px;
    border-radius: 8px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

/* Hover effect */
.movie-card:hover {
    transform: scale(1.03);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    cursor: pointer;
}

/* Poster image */
.movie-card img {
    width: 100%;       /* fills card width */
    height: 300px;     /* fixed height */
    object-fit: cover; /* crop if needed */
    border-radius: 4px;
    display: block;
}

/* Title styling */
.movie-title {
    font-weight: 700;
    font-size: 0.85rem;
    line-height: 1.2em;
    height: 2.4em;
    overflow: hidden;
    margin-top: 6px;
    color: #ffffff;              /* white title */
    font-family: "Consolas", "Courier New", monospace; /* techy */
    text-decoration: none;   /* explicitly remove underline */
}

/* Year styling */
.movie-year {
    font-size: 0.75rem;
    color: #bbb;
    text-decoration: none;   /* explicitly remove underline */
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_FILE)
    return df

df = load_data()

# -----------------------------
# CLEAN / PREP DATA
# -----------------------------

# Convert Year to numeric
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

# Combine Actor1–Actor10 if they exist
actor_cols = [col for col in df.columns if col.startswith("Actor")]

# Convert rating to float, coerce errors to NaN
df['imdbRating'] = pd.to_numeric(df['imdbRating'], errors='coerce')

if actor_cols:
    df["AllActors"] = df[actor_cols].fillna("").agg(", ".join, axis=1)
else:
    df["AllActors"] = df.get("Actors", "")

# -----------------------------
# Set up Session State
# -----------------------------
if "random_mode" not in st.session_state:
    st.session_state.random_mode = False

if "random_selection" not in st.session_state:
    st.session_state.random_selection = None

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filter Movies")

# Search box
search_query = st.sidebar.text_input("Search Title")

# Genre filter
all_genres = sorted(
    set(g.strip() for genres in df["Genre"].dropna()
        for g in genres.split(","))
)
selected_genres = st.sidebar.multiselect("Genre", all_genres)

# Actor filter
all_actors = sorted(
    set(a.strip() for actors in df["AllActors"].dropna()
        for a in actors.split(",") if a.strip())
)
selected_actors = st.sidebar.multiselect("Actor", all_actors)

# Year filter
min_year = int(df["Year"].min())
max_year = int(df["Year"].max())
year_range = st.sidebar.slider("Year Range", min_year, max_year, (min_year, max_year))

# Sort option
sort_option = st.sidebar.selectbox(
    "Sort by:",
    options=[
        "Title", 
        "Year", 
        "IMDB Rating"
    ],
    index=0
)

# Random button
st.sidebar.markdown("---")
st.sidebar.subheader("🎲 Random Selection")

num_random = st.sidebar.number_input(
    "Number of random movies",
    min_value=1,
    max_value=50,
    value=5
)

pick_random = st.sidebar.button("Pick Random Movies")
clear_random = st.sidebar.button("Clear Random Mode")

# -----------------------------
# APPLY FILTERS
# -----------------------------
filtered_df = df.copy()

# Title search filter (case-insensitive substring match)
if search_query:
    filtered_df = filtered_df[
        filtered_df["Title"].str.contains(search_query, case=False, na=False)
    ]

# Genre filter
if selected_genres:
    filtered_df = filtered_df[
        filtered_df["Genre"].apply(
            lambda x: any(g in x for g in selected_genres) if pd.notna(x) else False
        )
    ]

# Actor filter
if selected_actors:
    filtered_df = filtered_df[
        filtered_df["AllActors"].apply(
            lambda x: any(a in x for a in selected_actors) if pd.notna(x) else False
        )
    ]

# Year filter
filtered_df = filtered_df[
    (filtered_df["Year"] >= year_range[0]) &
    (filtered_df["Year"] <= year_range[1])
]

# Sort
if sort_option == "Title":
    filtered_df = filtered_df.sort_values("Title")
elif sort_option == "Year":
    filtered_df = filtered_df.sort_values("Year")
elif sort_option == "IMDB Rating":
    filtered_df = filtered_df.sort_values("imdbRating", ascending=False)

# ----------------------------
# Filter check
# ----------------------------
if len(filtered_df) == 0:
    st.sidebar.warning("No movies match current filters.")

# -----------------------------
# HANDLE RANDOM MODE
# -----------------------------

# Initialize session state once
if "random_mode" not in st.session_state:
    st.session_state.random_mode = False

if "random_selection" not in st.session_state:
    st.session_state.random_selection = None

# Pick random
if pick_random and len(filtered_df) > 0:
    sample_size = min(num_random, len(filtered_df))
    st.session_state.random_selection = filtered_df.sample(n=sample_size)
    st.session_state.random_mode = True

# Clear random
if clear_random:
    st.session_state.random_mode = False
    st.session_state.random_selection = None


# -----------------------------
# DISPLAY POSTER GRID
# -----------------------------
st.write(f"### Showing {len(filtered_df)} movies")

cols = st.columns(5)

# If random button clicked, sample from filtered set
if st.session_state.random_mode and st.session_state.random_selection is not None:
    display_df = st.session_state.random_selection
    st.markdown("### 🎲 Random Mode Active")
else:
    display_df = filtered_df

for i, (_, row) in enumerate(display_df.iterrows()):
    with cols[i % 5]:

        imdb_id = row.get("imdbID", "")
        imdb_url = f"https://www.imdb.com/title/{imdb_id}/"

        # Shorten title if too long
        if len(row['Title']) > 25:
            title = f"{row['Title'][:16]}...{row['Title'][-4:]}"
        else:
            title = row['Title']

        # Poster HTML
        poster_html = ""
        if pd.notna(row["Poster"]) and row["Poster"] != "N/A":
            poster_html = f'<img src="{row["Poster"]}">'

        # Full card HTML in ONE markdown block
        card_html = f"""
        <a href="{imdb_url}" target="_blank" class="movie-link">
            <div class="movie-card">
                {poster_html}
                <div class="movie-title">{title}</div>
                <div class="movie-year">{int(row['Year']) if pd.notna(row['Year']) else ''}</div>
            </div>
        </a>
        """

        st.markdown(card_html, unsafe_allow_html=True)