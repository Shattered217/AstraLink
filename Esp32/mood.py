import urequests
import time

SERVER_URL = 'http://192.168.101.246:5000/mood'

def send_mood(mood):
    headers = {'Content-Type': 'application/json'}
    data = {'mood': mood}
    try:
        response = urequests.post(SERVER_URL, json=data, headers=headers)
#         print('Server response:', response.text)
        response.close()
    except Exception as e:
        print('Error sending data:', e)

# moods = ["cool", "laughing", "smiling", "kissing", "tasty", "thinking", "smirking", "shushing", "surprised"]
# for mood in moods:
#     send_mood(mood)
#     time.sleep(15)