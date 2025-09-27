from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3
import requests
from flask_cors import CORS
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={r"/*": {"origins": "*"}})

DB_NAME = "krishi_margam.db"
WEATHER_API_KEY = "8da6f6ca6aa97a5ca45da9dd4971b32b"  # replace with your real key

AUDIO_DIR = os.path.join(app.root_path, 'static', 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

# Simple assistant (keeps previous logic)
class MalayalamKrishiAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def speech_to_text(self, audio_data):
        try:
            text = self.recognizer.recognize_google(audio_data, language='ml-IN')
            return text
        except sr.UnknownValueError:
            return "ശബ്ദം മനസ്സിലാക്കാൻ കഴിഞ്ഞില്ല"
        except sr.RequestError as e:
            return f"എറർ: {str(e)}"

    def text_to_speech(self, text):
        try:
            # create a predictable filename in static/audio
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
            filename = f"resp_{timestamp}.mp3"
            filepath = os.path.join(AUDIO_DIR, filename)
            tts = gTTS(text=text, lang='ml', slow=False)
            tts.save(filepath)
            return filename
        except Exception as e:
            print(f"Text-to-speech error: {e}")
            return None

    # simplified weather translation and query
    def get_weather_info_malayalam(self, location):
        if WEATHER_API_KEY == "8da6f6ca6aa97a5ca45da9dd4971b32b":
            return "കാലാവസ്ഥാ API കീ സജ്ജമല്ല"
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                return f"{location}-ൽ ഇപ്പോൾ താപനില {temp}°C ആണ്. കാലാവസ്ഥ: {desc}. ആർദ്രത: {humidity}%"
            else:
                return f"{location}-ന്റെ കാലാവസ്ഥ ലഭിച്ചില്ല"
        except Exception as e:
            return f"കാലാവസ്ഥ വിവരം Error: {str(e)}"

    def process_malayalam_query(self, text, farmer_context=None):
        text_lower = text.lower()
        if 'കാലാവസ്ഥ' in text_lower or 'താപനില' in text_lower:
            if farmer_context and farmer_context.get('location'):
                return self.get_weather_info_malayalam(farmer_context['location'])
            else:
                return "കാലാവസ്ഥാ വിവരത്തിന് സ്ഥലനാമം തരൂ. ഉദാഹരണം: 'കൊച്ചി കാലാവസ്ഥ?'"
        if 'നമസ്കാരം' in text_lower or 'ഹലോ' in text_lower:
            return "നമസ്കാരം! ഞാൻ കൃഷി മാർഗം AI അസിസ്റ്റന്റ്. എന്ത് സഹായം വേണം?"
        return f"നിങ്ങൾ പറഞ്ഞത്: '{text}'. സഹായത്തിനായി 'സഹായം' എന്ന് ടൈപ്പ് ചെയ്യൂ."

assistant = MalayalamKrishiAssistant()

def init_db():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT,
            location TEXT,
            soil_type TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            crop_name TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY(farmer_id) REFERENCES farmers(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER,
            user_input TEXT,
            ai_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index3.html')

# Combined register: create user and farmer and return both ids
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password', 'farmerpass')
    name = data.get('name', '')
    location = data.get('location', '')
    soil_type = data.get('soil_type', '')
    if not username:
        return jsonify({"error": "Missing phone/username"}), 400
    try:
        with sqlite3.connect(DB_NAME, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO farmers (user_id, name, location, soil_type) VALUES (?, ?, ?, ?)",
                           (user_id, name, location, soil_type))
            farmer_id = cursor.lastrowid
            conn.commit()
        return jsonify({"message": "Registration successful", "user_id": user_id, "farmer_id": farmer_id}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password', 'farmerpass')
    if not username:
        return jsonify({"error": "Missing username"}), 400
    try:
        with sqlite3.connect(DB_NAME, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
            row = cursor.fetchone()
            if row:
                return jsonify({"message": "Login successful", "user_id": row[0]}), 200
            else:
                return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_farmer/<user_id>', methods=['GET'])
def get_farmer(user_id):
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, location, soil_type FROM farmers WHERE user_id=?", (user_id,))
        farmer = cursor.fetchone()
        conn.close()
        if farmer:
            return jsonify({"farmer_id": farmer[0], "name": farmer[1], "location": farmer[2], "soil_type": farmer[3]})
        else:
            return jsonify({"error": "Farmer not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_weather/<location>', methods=['GET'])
def get_weather(location):
    # If API key not configured, return helpful message
    if WEATHER_API_KEY == "8da6f6ca6aa97a5ca45da9dd4971b32b":
        return jsonify({"error": "API key not configured."}), 500
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            data = response.json()
            result = {
                "location": data.get("name"),
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"]
            }
            return jsonify(result)
        else:
            return jsonify({"error": "Unable to fetch weather data"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_soil_info/<soil_id>', methods=['GET'])
def get_soil_info(soil_id):
    soil_data = {
        "black": "Rich in clay, ideal for cotton.",
        "red": "Suitable for groundnut, millets, pulses.",
        "alluvial": "Fertile, good for rice, wheat, sugarcane.",
        "laterite": "Good for tea, coffee, cashew."
    }
    info = soil_data.get(soil_id.lower(), "No data available")
    return jsonify({"soil_type": soil_id, "info": info})

@app.route('/add_activity', methods=['POST'])
def add_activity():
    data = request.get_json() or {}
    farmer_id = data.get("farmer_id")
    activity_type = data.get("activity_type")
    crop_name = data.get("crop_name")
    date = data.get("date") or datetime.now().isoformat()
    notes = data.get("notes")
    if not farmer_id:
        return jsonify({"error": "Missing farmer_id"}), 400
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activities (farmer_id, activity_type, crop_name, date, notes) VALUES (?, ?, ?, ?, ?)",
                       (farmer_id, activity_type, crop_name, date, notes))
        conn.commit()
        conn.close()
        return jsonify({"message": "Activity added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_activity/<farmer_id>', methods=['GET'])
def get_activity(farmer_id):
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT activity_type, crop_name, date, notes FROM activities WHERE farmer_id=?", (farmer_id,))
        rows = cursor.fetchall()
        conn.close()
        activities = [{"activity_type": row[0], "crop_name": row[1], "date": row[2], "notes": row[3]} for row in rows]
        return jsonify(activities)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Speech to text (expects file field 'audio')
@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'ഓഡിയോ ഫയൽ കണ്ടെത്തിയില്ല'})
        audio_file = request.files['audio']
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio_file.save(temp_audio.name)
        with sr.AudioFile(temp_audio.name) as source:
            audio_data = assistant.recognizer.record(source)
            text = assistant.speech_to_text(audio_data)
        os.unlink(temp_audio.name)
        return jsonify({'success': True, 'text': text})
    except Exception as e:
        return jsonify({'success': False, 'error': f'എറർ: {str(e)}'})

@app.route('/ai_assistant', methods=['POST'])
def ai_assistant():
    try:
        data = request.get_json() or {}
        user_input = data.get('text', '')
        farmer_id = data.get('farmer_id')
        if not user_input:
            return jsonify({'success': False, 'error': 'Input missing'}), 400

        farmer_context = None
        if farmer_id:
            conn = sqlite3.connect(DB_NAME, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT name, location, soil_type FROM farmers WHERE id=?", (farmer_id,))
            farmer_data = cursor.fetchone()
            conn.close()
            if farmer_data:
                farmer_context = {'name': farmer_data[0], 'location': farmer_data[1], 'soil_type': farmer_data[2]}

        response_text = assistant.process_malayalam_query(user_input, farmer_context)
        audio_filename = assistant.text_to_speech(response_text)  # returns filename in static/audio or None

        conn = sqlite3.connect(DB_NAME, timeout=10)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ai_queries (farmer_id, user_input, ai_response) VALUES (?, ?, ?)",
                       (farmer_id, user_input, response_text))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'text_response': response_text, 'audio_response': audio_filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
