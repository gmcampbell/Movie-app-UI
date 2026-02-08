import streamlit as st
import pandas as pd
import math

# Author Greg Campbell - see MIT License in repository
# Written with assistance from ChatGPT (GPT-5.2)
# -----------------------------
# History
# -----------------------------
# 2026-01-31: Initial version (actor, genre, year filters; sort; poster grid)
# 2026-02-01: Added random mode, mouse-over effects, IMDB links, rating filter
# 2026-02-02: Updated home database, fixed mobile layout
# 2026-02-03: Added runtime filter
# 2026-02-04: Added franchise detection and filters (HP, SW, Bond), can sort after random

# -----------------------------
# USAGE:
# -----------------------------
## In terminal:
## Installs if needed:
### pip install streamlit pandas 
## Run app:
### streamlit run movie_app.py

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
    /* height: 300px;     /* fixed height */ */
    height: auto;
    aspect-ratio: 2/3; /* maintain 2:3 ratio */
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

# Convert runtime to float, coerce errors to NaN
# remove ' min' if it exists, then convert
df['Runtime'] = df['Runtime'].astype(str).str.replace(' min', '', regex=False)
df['Runtime'] = pd.to_numeric(df['Runtime'], errors='coerce')

if actor_cols:
    df["AllActors"] = df[actor_cols].fillna("").agg(", ".join, axis=1)
else:
    df["AllActors"] = df.get("Actors", "")

# refine titles for sorting
def normalize_title(title):
    if not isinstance(title, str):
        return ""
    title = title.strip()
    if title.lower().startswith("the "):
        return title[4:]
    return title

# Franchise detection keywords
def detect_franchise(plot, keywords):
    if not isinstance(plot, str):
        return False
    plot = plot.lower()
    return any(keyword in plot for keyword in keywords)

franchises = {
    "Harry Potter": ["harry potter", "hogwarts", "voldemort"],
    "Star Wars": ["star wars", "jedi", "sith", "skywalker", "death star"],
    "James Bond": ["james bond", "007", "mi6"]
}

for name, keywords in franchises.items():
    df[name] = df["Plot"].apply(lambda x: detect_franchise(x, keywords))

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

# Sort option
sort_option = st.sidebar.selectbox(
    "Sort by:",
    options=[
        "Title", 
        "Year", 
        "IMDB Rating",
        "Runtime"
    ],
    index=0
)

# Year filter
min_year = int(df["Year"].min())
max_year = int(df["Year"].max())
year_range = st.sidebar.slider("Year Range", min_year, max_year, (min_year, max_year))

# Runtime filter
min_runtime = int(df["Runtime"].min())
max_runtime = int(df["Runtime"].max())
runtime_range = st.sidebar.slider("Runtime Range (minutes)", min_runtime, max_runtime, (min_runtime, max_runtime))

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

# Series filter
st.sidebar.header("Franchise Filters, Include:")

include_hp = st.sidebar.checkbox("Harry Potter", value=True)
include_sw = st.sidebar.checkbox("Star Wars", value=True)
include_bond = st.sidebar.checkbox("James Bond", value=True)

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

# Runtime filter
filtered_df = filtered_df[
    (filtered_df["Runtime"] >= runtime_range[0]) &
    (filtered_df["Runtime"] <= runtime_range[1])
]

# for franchise in selected_franchise:
#     filtered_df = filtered_df[~filtered_df[franchise]]
# Franchise filters
if not include_hp:
    filtered_df = filtered_df[~filtered_df["Harry Potter"]]
if not include_sw:
    filtered_df = filtered_df[~filtered_df["Star Wars"]]
if not include_bond:
    filtered_df = filtered_df[~filtered_df["James Bond"]]

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

# If random button clicked, sample from filtered set
if st.session_state.random_mode and st.session_state.random_selection is not None:
    display_df = st.session_state.random_selection
    st.markdown("### 🎲 Random Mode Active")
else:
    display_df = filtered_df

# -----------------------------
# SORTING
# -----------------------------
# Sort
if sort_option == "Title":
    display_df["sort_title"] = display_df["Title"].apply(normalize_title)
    display_df = display_df.sort_values("sort_title")
    display_df = display_df.drop(columns=["sort_title"])
elif sort_option == "Year":
    display_df = display_df.sort_values("Year")
elif sort_option == "IMDB Rating":
    display_df = display_df.sort_values("imdbRating", ascending=False)
elif sort_option == "Runtime":
    display_df = display_df.sort_values("Runtime")


# -----------------------------
# DISPLAY POSTER GRID
# -----------------------------
st.write(f"### Choosing from {len(filtered_df)} movies")

# if st.query_params.get("mobile") == "1":
#     num_cols = 1
# else:
num_cols = 5
cols = st.columns(num_cols)

num_cols = 5

# Display in grid by rows (scales if unable to get up to num_cols)
for i in range(0, len(display_df), num_cols):
    row_slice = display_df.iloc[i:i+num_cols]
    cols = st.columns(num_cols)

    for col, (_, row) in zip(cols, row_slice.iterrows()):
        with col:
            imdb_id = row.get("imdbID", "")
            imdb_url = f"https://www.imdb.com/title/{imdb_id}/"

            # Shorten title if too long
            if len(row['Title']) > 25:
                title = f"{row['Title'][:18]}...{row['Title'][-6:]}"
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