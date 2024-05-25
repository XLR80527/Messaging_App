'''
socket_routes
file containing all the routes related to socket.io
'''

from sqlalchemy.orm import Session
from flask_socketio import join_room, emit, leave_room
from flask import request, jsonify

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room, MessageHistory

import db
room = Room()

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))
    

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))


@socketio.on("delete_online")
def delete_online(username):
    db.remove_online_user(username)

# get the key
@socketio.on("getkey")
def getkey(username):
    user = db.get_user(username)
    emit("key", (user.password)) 

@socketio.on("historykey")
def getkey(username, message):
    user = db.get_user(username)
    emit("gethistory", (username, user.password, message)) 

# send message event handler
@socketio.on("send")
def send(username, encrypted, signature, key, room_id):
    client_user = room.get_room_client_user(room_id)
    room_user = room.get_room_user(room_id)
    for user in room_user:
        if user not in client_user:
            db.add_leaving_message_user(user, username)
    emit("incoming_send", (username, encrypted, signature, key), to=int(room_id))    


@socketio.on("get_leaving_user")
def get_leaving_user():
    leaving_user = db.get_leaving_message_user()
    emit("leaving_user", (leaving_user))    

# get the history
@socketio.on("history")
def history(username, message, room_id):
    chat = MessageHistory(sender=username, message=message, room_id=room_id)
    with Session(db.engine) as session:
        session.add(chat)
        session.commit()

# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    found = False
    
    friendlist = db.get_friend_list(sender_name)
    for item in friendlist:
        if item == receiver_name:
            found = True
            break
    if found is False:
        return "Not friend yet."

    room_id = db.get_room(receiver_name)
    room_id2 = db.get_room(sender_name)
    if room_id is not None or room_id2 is not None :
        if room_id is None:
            room_id = room_id2
    # if the user is already inside of a room 
    if room_id is not None:
        room.join_room(sender_name, receiver_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        # emit only to the sender
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        db.remove_leaving_message_user(sender_name)
        with Session(db.engine) as session:
            message_history = session.query(MessageHistory).filter_by(room_id=room_id).all()
        
        for message in message_history:
            emit("incoming_history", (message.sender,message.message))
        return room_id

    # if the user isn't inside of any room, 
    # perhaps this user has recently left a room
    # or is simply a new user looking to chat with someone
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    db.update_room(sender_name, receiver_name, room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    return room_id

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)


@socketio.on('get_user_role')
def get_user_role(username):
    user = db.get_user(username)
    emit("user_role", (user.role))

@socketio.on("history_check")
def get_user_role(username):
    user = db.get_user(username)
    with Session(db.engine) as session:
        message_history = session.query(MessageHistory).filter_by(room_id=user.room).all()
        
        for message in message_history:
            emit("history_decode", (message.sender,message.message))


@socketio.on("gethistorykey")
def getkey(username, message):
    user = db.get_user(username)
    emit("history_search", (username, user.password, message)) 

@socketio.on("offlinemessages")
def offline_messages(username):
    offline_messages_user = db.get_leaving_message_user(username)
    for user in offline_messages_user:
        offline_message_str  = user + " left you a message."
        emit("show_offline_messages", (offline_message_str))
