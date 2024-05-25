'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import Column, String, Integer, BINARY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Dict

# data models
class Base(DeclarativeBase):
    pass

# model to store user information
class User(Base):
    __tablename__ = "user"
    
    # looks complicated but basically means
    # I want a username column of type string,
    # and I want this column to be my primary key
    # then accessing john.username -> will give me some data of type string
    # in other words we've mapped the username Python object property to an SQL column of type String 
    username: Mapped[str] = mapped_column(String, primary_key=True)
    password: Mapped[BINARY] = mapped_column(BINARY)
    salt: Mapped[BINARY] = mapped_column(BINARY)
    friend: Mapped[str] = mapped_column(String)
    room: Mapped[Integer] = mapped_column(Integer)
    sent_request: Mapped[str] = mapped_column(String)
    received_request: Mapped[str] = mapped_column(String)
    js_salt: Mapped[str] = mapped_column(String)
    js_hash: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    article: Mapped[str] = mapped_column(String)
    mute_status: Mapped[str] = mapped_column(String)

    

# stateful counter used to generate the room id
class Counter():
    def __init__(self):
        self.counter = 0
    
    def get(self):
        self.counter += 1
        return self.counter



# Room class, used to keep track of which username is in which room
class Room():
    def __init__(self):
        self.counter = Counter()
        self.room_id = self.counter.get() 
        # dictionary that maps the username to the room id
        # for example self.dict["John"] -> gives you the room id of 
        # the room where John is in
        self.dict: Dict[str, int] = {}
        self.room_data: Dict[int, str] = {} 
        self.room_user: Dict[str, int] = {}
        self.client_user: Dict[str, int] = {}

    def create_room(self, sender: str, receiver: str) -> int:
        room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        self.room_user[sender] = room_id
        self.room_user[receiver] = room_id
        self.room_data[room_id] = receiver
        self.client_user[sender] = room_id
        return room_id
    
    def join_room(self, sender: str, receiver: str, room_id: int) -> int:
        self.dict[sender] = room_id
        self.client_user[sender] = room_id
        if receiver not in self.room_user.keys():
            self.room_user[receiver] = room_id
        if sender not in self.room_user.keys():
            self.room_user[sender] = room_id
        

    def leave_room(self, user):
        if user not in self.dict.keys():
            return
        del self.dict[user]
        del self.client_user[user]

    # gets the room id from a user
    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]

    # gets the receiver username
    def get_receiver_username(self, room_id):
        return self.room_data.get(room_id)
    
    def get_room_user(self, room_id):
        user_list = []
        for username, usr_room_id in self.room_user.items():
            if usr_room_id == room_id:
                user_list.append(username)
        return user_list

    def get_room_client_user(self, room_id):
        client_user_list = []
        for username, usr_room_id in self.client_user.items():
            if usr_room_id == room_id:
                client_user_list.append(username)
        return client_user_list
    

# Model to store message history
class MessageHistory(Base):
    __tablename__ = "message_history"
    
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer)
    sender = Column(String)
    message = Column(String)


# Model to store online user
class Onlinelist(Base):
    __tablename__ = "online_user"
    
    user = Column(String, primary_key=True)

# Model to store leaving message user
class LeavingMessage(Base):
    __tablename__ = "leaving_message_user"
    
    id = Column(Integer, primary_key=True)
    user = Column(String)
    sender = Column(String)
