from flask import Flask, request, jsonify
import threading

app = Flask(__name__)
current_mood = "default"
lock = threading.Lock()

valid_moods = [
    "cool", "laughing", "smiling", "kissing", "tasty",
    "thinking", "smirking", "shushing", "surprised"
]

@app.route('/mood', methods=['POST'])
def receive_mood():
    global current_mood
    if not request.is_json:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    data = request.get_json()
    mood_text = data.get("mood", "default")

    if mood_text in valid_moods:
        with lock:
            current_mood = mood_text
            print(f"Received new mood: {mood_text}")
        return jsonify({"status": "success", "mood": mood_text})
    else:
        with lock:
            current_mood = "default"
            print(f"Unknown mood: {mood_text}. Falling back to default.")
        return jsonify({"status": "error", "message": "Unknown mood", "mood": "default"})

@app.route('/get_mood', methods=['GET'])
def get_mood():
    with lock:
        return jsonify({"mood": current_mood})

def run_server():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    run_server()