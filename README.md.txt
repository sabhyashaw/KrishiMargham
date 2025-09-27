Overview

Farming Assistant is a web application designed to help farmers manage their farm activities efficiently while providing real-time Malayalam AI assistance. The application includes features like weather updates, soil information, crop advice, activity logging, and voice interaction in Malayalam.



Features

1.User Authentication

Register new farmers

Login existing farmers

2.Dashboard

View weather information based on location

Get soil type information

Log farm activities (Planting, Irrigation, Fertilization, Harvesting)

3.Malayalam AI Assistant

Text and voice-based AI queries

Speech-to-text conversion

AI responds with text and audio in Malayalam

4.Activity History

Track logged activities

Track AI queries


Tech Stack

Frontend: HTML, CSS (Bootstrap 5), JavaScript

Backend: Python (Flask)

Database: SQLite

AI / Voice:

Google Speech Recognition (Malayalam)

gTTS for text-to-speech (Malayalam)


Setup Instructions

1. Clone / Download the Project

Download all frontend and backend files into a folder on your local machine.


2. Install Python Dependencies

Open terminal/command prompt in your project folder and run:

pip install flask flask-cors requests speechrecognition gtts

Ensure Python 3.8+ is installed.


3. Backend Setup

The backend file (e.g., app_backened.py) contains all Flask routes.

Initialize the database and tables by running:

python app_backened.py

This will start the backend server at http://127.0.0.1:5000/ and automatically create SQLite tables if not present.


4. Frontend Setup

Save the frontend HTML file (e.g., index.html) in the same folder or a separate templates/ folder.

Open the frontend in a browser.

Important: Make sure all fetch URLs match your backend routes, e.g.:

fetch("http://127.0.0.1:5000/register", {...})
fetch("http://127.0.0.1:5000/login", {...})
fetch("http://127.0.0.1:5000/ai_assistant", {...})


5. Running the Application

Start the backend server:

python app_backened.py

Open index.html in your browser.

Register a new farmer or login using a phone number.

Access the dashboard to check weather, soil info, activity logging, and Malayalam AI assistant.


Configuration

• Backend port: 5000 • Weather API: Replace WEATHER_API_KEY in backend.py with your
OpenWeatherMap API key.


Folder Structure (Example)

project-folder/
│
├─ app_backened.py
├─ krishi_margam.db   # Auto-created
├─ index.html         # Frontend file
├─ README.md
└─ assets/            # Optional: images, CSS, JS files



Troubleshooting

Frontend fetch not working:
Ensure backend server is running and fetch URLs point to correct port (http://127.0.0.1:5000/...).

Speech-to-text issues:
Check microphone permissions and browser compatibility.

Weather API not responding:
Replace placeholder API key with a valid OpenWeatherMap key.