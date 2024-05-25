'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, session, jsonify
from flask_socketio import SocketIO
import db
import secrets
import os
import hashlib
from datetime import timedelta
# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

app.permanent_session_lifetime = timedelta(minutes=10)

# don't remove this!!
import socket_routes

@app.route("/get_mute_status", methods = ["POST"])
def get_mute_status():
    username = request.json.get("username")
    return db.get_mute_status(username)


@app.route("/get_role", methods = ["POST"])
def get_role():
    username = request.json.get("username")
    return db.get_role(username)

# knowledge repository
@app.route("/knowledge_repository")
def knowledge_repository():
    if request.args.get("username") is None:
        abort(404)
    if db.get_user(request.args.get('username')) is None:
        abort(404)
    return render_template('knowledge_repository.jinja', username=request.args.get("username"))

@app.route("/knowledge", methods = ["POST"])
def knowledge():
    return url_for('knowledge_repository', username=request.json.get("username"))


@app.route("/Mute", methods = ["POST"])
def Mute():
    username = request.json.get('username')
    db.Mute(username)
    return '1'



@app.route("/Unmute", methods = ["POST"])
def Unmute():
    username = request.json.get('username')
    db.Unmute(username)
    return '1'


@app.route("/Add_comment", methods = ["POST"])
def Add_comment():
    username = request.json.get('username')
    comment_user = request.json.get('comment_user')
    title = request.json.get('title')
    comment = request.json.get('comment')
    db.Add_comment(username, comment_user, title, comment)
    return '1'


@app.route("/Delete_comment", methods = ["POST"])
def Delete_comment():
    username = request.json.get('username')
    title = request.json.get('title')
    comment = request.json.get('comment')
    db.Delete_comment(username, title, comment)
    return '1'


@app.route("/Modify", methods = ["POST"])
def Modify():
    username = request.json.get('username')
    title = request.json.get('title')
    modified_title = request.json.get('modified_title')
    modified_article = request.json.get('modified_article')
    db.Modify(username, title, modified_title, modified_article)
    return '1'


@app.route("/check_modify", methods = ["POST"])
def check_modify():
    username = request.json.get('username')
    title = request.json.get('title')
    modified_title = request.json.get('modified_title')
    return db.check_modify(username, title, modified_title)

@app.route("/get_before_modify", methods = ["POST"])
def get_before_modify():
    username = request.json.get('username')
    title = request.json.get('title')
    return db.get_before_modify(username, title)
    

@app.route("/Delete", methods = ["GET"])
def Delete():
    username = request.args.get('username')
    title = request.args.get('title')
    db.Delete(username, title)
    return "1"


@app.route("/check_title", methods = ["POST"])
def check_title():
    username = request.json.get('username')
    title = request.json.get('title')
    return db.check_title(username, title)


@app.route("/get_article", methods = ["POST"])
def get_article():
    username = request.json.get('username')
    title = request.json.get('title')
    return db.get_article(username, title)

@app.route("/get_comment", methods = ["POST"])
def get_comment():
    username = request.json.get('username')
    title = request.json.get('title')
    return db.get_comment(username, title)



@app.route("/update_title", methods = ["POST"])
def update_title():
    username = request.json.get('username')
    return db.get_all_title(username)

@app.route("/post", methods = ["GET"])
def post():
    username = request.args.get('user')
    title = request.args.get('title')
    article = request.args.get('article')
    db.post(username, title, article)
    return ""

@app.route("/get_js_salt")
def get_js_salt():
    username = request.args.get('user')
    user = db.get_user(username)
    if user != None:
        return user.js_salt
    return "FALSE"



@app.route("/check_user", methods = ["POST"])
def check_user():
    user = request.args.get('user')
    if db.get_user(user) == None:
        return "FALSE"
    return "TRUE"

@app.route("/check_user1", methods = ["POST"])
def check_user1():
    username = request.json.get('username')
    if db.get_user(username) == None:
        return "FALSE"
    return "TRUE"


# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

@app.route("/update_request", methods = ["GET"])
def update_request():
    user = request.args.get('user')
    friend = request.args.get('friend')
    db.update_request(user, friend)
    return ""

@app.route("/delete_friend", methods = ["GET"])
def delete_friend():
    user = request.args.get('user')
    friend = request.args.get('friend')
    db.delete_friend(user, friend)
    return ""

@app.route("/add_sent_message", methods = ["GET"])
def add_sent_message():
    user = request.args.get('user')
    return db.get_sent(user)

@app.route("/add_received_message", methods = ["GET"])
def add_received_message():
    user = request.args.get('user')
    return db.get_received(user)

@app.route("/add_friend_message", methods = ["GET"])
def add_friend_message():
    user = request.args.get('user')
    return db.get_friend_list(user)

@app.route("/approve", methods = ["GET"])
def approve():
    user = request.args.get('user')
    friend = request.args.get('friend')
    return db.approve(user, friend)
    


@app.route("/reject", methods = ["GET"])
def reject():
    user = request.args.get('user')
    friend = request.args.get('friend')
    return db.reject(user, friend)
    

@app.route("/check_friend_exist", methods = ["GET"])
def check_friend_exist():
    user = request.args.get('user')
    friend = request.args.get('friend')
    return db.check_friend_exist(user, friend)

@app.route('/online_users', methods=['GET'])
def online_users():
    online_users = db.get_online_users()
    return jsonify({'online_users': online_users})

@app.route('/send', methods=['POST'] )
def send(): 
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    encrypted_message = request.json.get("message")
    signature = request.json.get("signature")
    key = request.json.get("key")
    room_id = request.json.get("room_id")

    socketio.emit("incoming_send", (username, encrypted_message, signature, key), to=room_id)
    return ""

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    user =  db.get_user(username)
    if user is None:
        return "Error: User does not exist!"

    # Get the salt value from the database
    salt = user.salt

    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    if user.password != hashed_password:
        return "Error: Password does not match!"
    
    session["username"] = user.username
    db.add_online_user(username)
    
    return url_for('home', username=request.json.get("username"))

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")


@app.route('/check_cookie', methods=['GET'])
def check_cookie():
    current = request.args.get("username")
    user_cookie = session.get("username")
    if not user_cookie or str(user_cookie) != current:
        db.remove_online_user(current)
        return "FALSE"
    return "TRUE"


# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")
    js_salt = request.json.get("js_salt")
    js_hash = request.json.get("js_hash")
    role = request.json.get("role")
    # Generates a random salt
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    if db.get_user(username) is None:
        db.insert_user(username, hashed_password, salt, friend="",room=-1, sent_request="", received_request="",js_salt=js_salt, js_hash=js_hash, role = role, article="", title="", mute_status="FALSE")
        session["username"] = db.get_user(username).username
        db.add_online_user(username)
        return url_for('home', username=username)
    return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)
    if db.get_user(request.args.get('username')) is None:
        abort(404)
    return render_template("home.jinja", username=request.args.get("username"))
if __name__ == '__main__':
    socketio.run(app, ssl_context = ('./certs/CA2.pem', './certs/CA2-key.pem'))