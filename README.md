🎬 Movie Explorer UI

A Streamlit-based interactive movie browser built for your personal movie collection.
Browse, filter, sort, and randomly discover films in a clean, responsive interface.

🚀 Features

  🎥 Poster-based movie grid
  
  🔎 Search, Filtering, and Sorting
  
  🎲 Random movie selection mode
  
  🔗 Clickable cards linking directly to IMDb

📂 Project Structure
movie-app-ui/
│
├── movie_app.py           - Streamlit UI

├── database_setup.ipynb   - use OMDB API to turn a list to a database

├── Example_movies.txt     - make youre own

├── movie_database.csv     - updates from database_setup

├── requirements.txt 

├── README.md

└── .gitignore

⚙️ Running Locally

Your TODO:
- Clone
- Install dependencies:
    pip install -r requirements.txt
- Make your database

    create your own .txt with titles/IMDB ID's
  
    make an OMDB API - https://www.omdbapi.com/apikey.aspx
  
    update API variable and 'run all' through database_setup.ipynb
  
    correct titles in .txt that raise errors
- Run your UI locally
  
    in terminal:
  
      streamlit run app.py

- Open in your browser:
  
    http://localhost:8501

🌎 Accessing remotely (or on mobile):

I host a local 'zrok' to provide online access (I'm using 1.0, feel free to try 2.0):

  Download/Install Zrok:
  - https://www.youtube.com/watch?v=Je5j4ThouCo

  Make an account:
  - https://netfoundry.io/docs/zrok/1.0/getting-started 
    
  Run in terminal (command prompt):
  
    zrok enable 'key_here'
    
    zrok share public 8051
    
  Send yourself the zrok link!

📸 UI Screenshot:

  <img width="1785" height="866" alt="image" src="https://github.com/user-attachments/assets/9eb3ffe9-0fcf-4384-9255-8cce0d9ddd8c" />


