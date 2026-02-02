🎬 Movie Explorer UI

A Streamlit-based interactive movie browser built from a curated IMDb dataset.
Browse, filter, sort, and randomly discover films in a clean, responsive interface.

🔗 Live App: Coming Soon.

🚀 Features

  🎥 Poster-based movie grid
  
  🔎 Search by title
  
  🎭 Filter by genre
  
  🎬 Filter by actor
  
  📅 Filter by year range
  
  ⭐ Sort by IMDb rating
  
  🎲 Random movie selection mode

  🔗 Clickable cards linking directly to IMDb

🛠 Tech Stack

Python

Streamlit

Pandas

IMDb data via pre-built dataset (generated separately)

📂 Project Structure
movie-app-ui/
│
├── app.py
├── movies.csv
├── requirements.txt
├── README.md
└── .gitignore

⚙️ Running Locally

Clone the repository:

git clone https://github.com/YOUR_USERNAME/movie-app-ui.git
cd movie-app-ui


Install dependencies:

pip install -r requirements.txt


Run the app:

streamlit run app.py


Open in your browser:

http://localhost:8501

🌐 Deployment

This app is deployed using Streamlit Community Cloud.

To deploy your own version:

Fork this repository

Connect it to Streamlit Cloud

Select app.py as the entry point

Deploy

🔐 Data Source

This UI consumes a pre-built movie dataset (movies.csv).
The data generation pipeline (OMDb API ingestion & cleaning) is maintained separately.
