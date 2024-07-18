from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import pywhatkit
import threading
import pyttsx3
import wikipedia
from datetime import datetime
 
app = Flask(__name__)
socketio = SocketIO(app)
 
# Initialize text-to-speech
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
talk_lock = threading.Lock()
 
def handle_voice_command(command):
    print(f"Input Command: {command}")  # Logging input command
    response_text = ""
    try:
        if 'play' in command:
            song = command.replace('play', '').strip()
            response_text = f'Playing {song}'
            talk(response_text)
            pywhatkit.playonyt(song)
        elif 'time' in command:
            now = datetime.now().strftime("%H:%M")
            response_text = f"The current time is {now}"
            talk(response_text)
        elif 'who is' in command:
            person = command.replace('who is', '').strip()
            try:
                summary = wikipedia.summary(person, sentences=2)
                response_text = summary
            except Exception as e:
                response_text = f"I couldn't find information about {person}"
            talk(response_text)
        elif 'joke' in command:
            response_text = "Why don't scientists trust atoms? Because they make up everything!"
            talk(response_text)
        else:
            response_text = 'Command not recognized. Please try again.'
            talk(response_text)
    except Exception as e:
        response_text = f"An error occurred: {str(e)}"
        talk(response_text)
    return response_text
 
def talk(text):
    with talk_lock:
        engine.say(text)
        engine.runAndWait()
 
@app.route('/')
def index():
    return render_template('index.html')
 
@socketio.on('voice_command')
def handle_voice_command_event(json):
    command = json.get('command', '')
    if command:
        response_text = handle_voice_command(command)
        emit('response', {'status': 'success', 'message': response_text})
 
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)