from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_socketio import SocketIO, send, emit
from datetime import datetime


app = Flask(__name__)
app.secret_key = "worst_admin"
socketio = SocketIO()
socketio.init_app(app)

def get_db():
    db = sqlite3.connect("data.db")
    return db
def create_db():
    db = get_db()
    cursor = db.cursor()

    # Create tables
    ## Messages
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, timestamp TEXT, original TEXT NOT NULL, accepted BOOLEAN, safe TEXT)")

    db.commit()
    db.close()
create_db()


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", messages=get_last_n_messages())


# SocketIO
## Initial Connection
@socketio.on("initial_connection")
def initialconnection(json):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    print(ip, str(json["data"]))
    # TODO make get last n function and return last 20 messages which the client will then display

## New message
@socketio.on("new_message")
def new_message(json):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.utcnow().isoformat()
    
    # Original message the user sent
    original = str(json["message"]).strip()
    print(ip,timestamp,"message:" ,original)
    
    # Input validation for original
    if not original or len(original) > 2000: # 2000 char limit per message
        emit("error", {"message": "Message too long (or empty)."}) # TODO display error on client
        return # Stops the rest of the function from running

    # boolean, AI(LLM or other) marks message as acceptable (1) or unacceptable (0)
    accepted = 1 if "badword" not in original.lower() else 0 
    # TODO AI(LLM or other) integration
 
    # safe, LLM rewritten version of accepted messages
    if accepted == 1:
        safe = original #TODO LLM integration
    else:
        safe = None # Just store the original message the AI(LLM or other) marked it for deletion so it didn't rewrite a safe version

    # Save to DB
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("INSERT INTO messages (ip, timestamp, original, accepted, safe) VALUES (?, ?, ?, ?, ?)", (ip, timestamp, original, accepted, safe))
    
    db.commit()
    db.close()
    
## Load older
# TODO when user scrolls back far enough return more older messages if any, if less than n messages (including 0 older messages) display a message so the user knows they have seen loaded all messages


# Error Handling
@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('index'))

# Database functions
## Get Last n messages TODO untested
def get_last_n_messages(n=20):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * from messages ORDER BY id DESC LIMIT ?", (n,))
    messages = cursor.fetchall()
    db.close()
    return messages[::-1] # Has oldest messages first