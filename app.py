from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_socketio import SocketIO#, send, emit


app = Flask(__name__)
app.secret_key = "worst_admin"
socketio = SocketIO()


def get_db():
    db = sqlite3.connect("data.db")
    return db
def create_db():
    db = get_db()
    cursor = db.cursor()

    # Create tables
    ## Messages
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, timestamp TEXT, original TEXT NOT NULL, censored TEXT, accepted BOOLEAN, safe TEXT)")


    db.commit()
    db.close()
create_db()
socketio.init_app(app)

@app.route("/", methods=["GET", "POST"])
def index():        
    return render_template("index.html")


# https://flask-socketio.readthedocs.io/en/latest/getting_started.html
# SocketIO
@socketio.on('message')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    print(user_ip)

## New message
@socketio.on('my event')
def handle_my_custom_event(data):
    emit('my response', data, broadcast=True)


# Error Handling
@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('index'))

# Database functions

