'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *


from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, hashed_password, salt, friend: str,room: int, sent_request: str, received_request: str, js_salt, js_hash, role, title, article, mute_status):
    with Session(engine) as session:
        user = User(username=username, salt=salt, password=hashed_password, friend=friend, room = room, sent_request = sent_request, received_request = received_request, js_salt = js_salt, js_hash = js_hash, role = role, title=title, article=article, mute_status=mute_status)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)

def update_room(user1: str, user2: str, room_id: int):
    with Session(engine) as session:
        user = get_user(user1)
        receiver = get_user(user2)
        if not user1 or not user2:
            return "error"
        user.room = room_id
        receiver.room = room_id
        session.delete(user)
        session.delete(receiver)
        session.add(user)
        session.add(receiver)
        session.commit()

def get_room(username: str):
    user = get_user(username)
    if user.room == -1:
        return None
    return user.room

def update_friend_list(username: str, friend: str):
    with Session(engine) as session:
        user = get_user(username)
        Friend = get_user(friend)
        if not user or not Friend:
            return "error"
        user.friend += Friend.username
        user.friend += " "
        Friend.friend += user.username
        Friend.friend += " "
        session.delete(user)
        session.delete(Friend)
        session.add(user)
        session.add(Friend)
        session.commit()

def delete_friend(username: str, friend: str):
    with Session(engine) as session:
        user = get_user(username)
        Friend = get_user(friend)
        if not user or not Friend:
            return "error"
        user.friend = user.friend[:-1]
        user.friend = user.friend.replace(Friend.username, "")
        Friend.friend = Friend.friend[:-1]
        Friend.friend = Friend.friend.replace(user.username, "")
        session.delete(user)
        session.delete(Friend)
        session.add(user)
        session.add(Friend)
        session.commit()

def update_request(username: str, friend: str):
    with Session(engine) as session:
        user = get_user(username)
        Friend = get_user(friend)
        if not user or not Friend:
            return "error"
        user.sent_request += "To-"
        user.sent_request += Friend.username
        user.sent_request += " "
        Friend.received_request += "From-"
        Friend.received_request += user.username
        Friend.received_request += " "
        session.delete(user)
        session.delete(Friend)
        session.add(user)
        session.add(Friend)
        session.commit()

def get_sent(username):
    user = get_user(username)
    s = user.sent_request
    s = s.strip()
    ls = s.split(" ")
    return ls

def get_received(username):
    user = get_user(username)
    s = user.received_request
    s = s.strip()
    ls = s.split(" ")
    return ls

def get_friend_list(username):
    user = get_user(username)
    s = user.friend
    s = s.strip()
    ls = s.split(" ")
    return ls

def approve(username, friend):
    with Session(engine) as session:
        user = get_user(username)
        name = user.received_request
        name = name.strip()
        name_ls = name.split(" ")
        name1 = name_ls[0]
        if name1 == "":
            return "FALSE"

        i = 0
        while i < len(name_ls):
            f_name = (name_ls[i].split("-"))[1] 
            if f_name == friend:
                name_ls.pop(i)
                user.friend += friend
                user.friend += " "
                break
            i += 1
        user.received_request = ""
        for i in name_ls:
            user.received_request += i
            user.received_request += " "

        user_send = get_user(friend)
        user_send.friend += username
        user_send.friend += " "

        sent = user_send.sent_request
        sent = sent.strip()
        sent_ls = sent.split(" ")
        for j in sent_ls:
            if j.count(username) > 0:
                sent_ls.remove(j)
                break
        user_send.sent_request = ""
        q = 0
        while q < len(sent_ls):
            user_send.sent_request += sent_ls[q]
            user_send.sent_request += " "
            q += 1
        
        session.delete(user)
        session.delete(user_send)
        session.add(user)
        session.add(user_send)
        session.commit()
    return "TRUE"

def reject(username, friend):
    with Session(engine) as session:
        user = get_user(username)
        name = user.received_request
        name = name.strip()
        name_ls = name.split(" ")
        name1 = name_ls[0]
        if name1 == "":
            return "FALSE"

        i = 0
        while i < len(name_ls):
            f_name = (name_ls[i].split("-"))[1] 
            if f_name == friend:
                name_ls.pop(i)
                break
            i += 1
        user.received_request = ""
        for i in name_ls:
            user.received_request += i
            user.received_request += " "

        user_send = get_user(friend)

        sent = user_send.sent_request
        sent = sent.strip()
        sent_ls = sent.split(" ")
        for j in sent_ls:
            if j.count(username) > 0:
                sent_ls.remove(j)
                break
        user_send.sent_request = ""
        q = 0
        while q < len(sent_ls):
            user_send.sent_request += sent_ls[q]
            user_send.sent_request += " "
            q += 1
        
        session.delete(user)
        session.delete(user_send)
        session.add(user)
        session.add(user_send)
        session.commit()
    return 'TRUE'


def check_friend_exist(username, Friend):
    user = get_user(username)
    f = user.friend
    f = f.strip()
    f_ls = f.split(" ")
    for i in f_ls:
        if i.count(Friend) > 0:
            return "TRUE"
    return "FALSE"

def get_js_salt(username):
    user = get_user(username)
    if user != None:
        return user.js_salt
    return None

def get_js_hash(username):
    user = get_user(username)
    if user != None:
        return user.js_hash
    return None

def add_leaving_message_user(username, sender):
    with Session(engine) as session:
        existing_record = session.query(LeavingMessage).filter_by(user=username, sender=sender).first()
        if existing_record:
            return
        user = LeavingMessage(user=username, sender=sender)
        session.add(user)
        session.commit()

def remove_leaving_message_user(username):
    with Session(engine) as session:
        users = session.query(LeavingMessage).filter(LeavingMessage.user == username).all()
        for user in users:
            session.delete(user)
        session.commit()

def get_leaving_message_user(username):
    with Session(engine) as session:
        users = session.query(LeavingMessage).filter_by(user=username).all()
        result_list = []
        for user in users:
            result_list.append(user.sender)
        session.commit()
        return result_list

def add_online_user(username):
    with Session(engine) as session:
        online_user = Onlinelist(user=username)
        session.add(online_user)
        session.commit()

def remove_online_user(username):
    with Session(engine) as session:
        user = session.query(Onlinelist).filter_by(user=username).first()
        if user:
            session.delete(user)
            session.commit()

def get_online_users():
    with Session(engine) as session:
        online_users = session.query(Onlinelist).all()
        return [user.user for user in online_users]
    


def post(username, title, article):
    with Session(engine) as session:
        user = get_user(username)
        user.title += title
        user.title += "---"
        user.title += username
        user.title += "("
        user.title += user.role
        user.title += ")"
        user.title += "!!"
        user.article += article
        user.article += "@@"
        user.title = user.title
        user.article = user.article
        session.delete(user)
        session.add(user)
        session.commit()

def get_all_title(username):
    user = get_user(username)
    ls = (user.title.strip("")).split("!!")
    f = user.friend
    f = f.strip("")
    f_ls = f.split(" ")

    for i in f_ls:
        if i.strip("") == "":
            continue
        friend = get_user(i)
        f_title = (friend.title).strip("")
        f_title_ls = f_title.split("!!")
        for q in f_title_ls:
            ls.append(q)
    
    l = 0
    while l < len(ls):
        if ls[l].strip("") == "":
            ls.pop(l)
            continue
        l += 1
    
    return ls

def get_article(username, title):
    user = get_user(username)
    t = user.title.strip("")
    t_ls = t.split("!!")

    l = 0
    while l < len(t_ls):
        if t_ls[l].strip("") == "":
            t_ls.pop(l)
            continue

        try:
            if t_ls[l+1].strip("") == "":
                t_ls.pop(l+1)
                continue
        except:
            break

        if (t_ls[l].split("---"))[0] == title:
            break
        l += 1
    
    a = user.article.strip("")
    a_ls = a.split("@@")

    q = 0
    while q < len(a_ls):
        if a_ls[q].strip("") == "":
            a_ls.pop(q)
            continue
        q += 1

    final_ls = a_ls[l].split("##")
    return final_ls[0]


def check_title(username, title):
    user = get_user(username)
    if not user:
        return "FALSE"
    t = user.title.strip("")
    t_ls = t.split("!!")
    for i in t_ls:
        if i.count(title) > 0:
            return "TRUE"
        
    return "FALSE"

def Delete(username, title):
    with Session(engine) as session:
        user = get_user(username)
        t = user.title.strip("")
        t_ls = t.split("!!")
        l = 0
        for i in t_ls:
            if i.split("---")[0] == title:
                t_ls.pop(l)
                break
            l += 1
        a = user.article.strip("")
        a_ls = a.split("@@")
        a_ls.pop(l)

        a1 = ""
        for q in a_ls:
            a1 += q
            a1 += "@@"

        t1 = ""
        for k in t_ls:
            t1 += k
            t1 += "!!"
        
        user.title = t1
        user.article = a1
        session.delete(user)
        session.add(user)
        session.commit()


def get_before_modify(username, title):
    user = get_user(username)
    t = user.title.strip("")
    t_ls = t.split("!!")

    l = 0
    while l < len(t_ls):
        if t_ls[l].strip("") == "":
            t_ls.pop(l)
            continue

        try:
            if t_ls[l+1].strip("") == "":
                t_ls.pop(l+1)
                continue
        except:
            break

        if (t_ls[l].split("---"))[0] == title:
            break
        l += 1

    title1 = t_ls[l]

    a = user.article.strip("")
    a_ls = a.split("@@")

    q = 0
    while q < len(a_ls):
        if a_ls[q].strip("") == "":
            a_ls.pop(q)
            continue
        q += 1
    final_ls = a_ls[l].split("##")
    final_ls1 = [(title1.split("---"))[0], final_ls[0]]
    return final_ls1

def Modify(username, title, modified_title, modified_article):
    with Session(engine) as session:
        user = get_user(username)
        modified_title += "---"
        modified_title += username
        modified_title += "("
        modified_title += user.role
        modified_title += ")"
        t = user.title.strip("")
        t_ls = t.split("!!")

        l = 0
        while l < len(t_ls):
            if t_ls[l].strip("") == "":
                t_ls.pop(l)
                continue

            try:
                if t_ls[l+1].strip("") == "":
                    t_ls.pop(l+1)
                    continue
            except:
                print("")
            
            if (t_ls[l].split("---"))[0] == title:
                t_ls[l] = modified_title
                break

            l += 1
        
        a = user.article.strip("")
        a_ls = a.split("@@")

        q = 0
        while q < len(a_ls):
            if a_ls[q].strip("") == "":
                a_ls.pop(q)
                continue
            q += 1
        
        a_ls1 = a_ls[l].split("##")
        a_ls1[0] = modified_article
        a1 = ""
        for i in a_ls1:
            a1 += i
            a1 += "##"
        a1 = a1.rstrip("##")
        a_ls[l] = a1
        
        t1 = ""
        for i in t_ls:
            t1 += i
            t1 += "!!"

        a2 = ""
        for i in a_ls:
            a2 += i
            a2 += "@@"
        
        user.title = t1
        user.article = a2
        print(user.title)
        print(user.article)
        session.delete(user)
        session.add(user)
        session.commit()

  
def check_modify(username, title, modified_title):
    user = get_user(username)
    t = user.title.strip("")
    t_ls = t.split("!!")
    l = 0
    while l < len(t_ls):
        if (t_ls[l].split("---"))[0] != title and (t_ls[l].split("---"))[0] == modified_title:
            return "FALSE"
        l += 1
    return "TRUE"

def Add_comment(username, comment_user, title, comment):
    with Session(engine) as session:
        user = get_user(username)
        t = user.title.strip("")
        t_ls = t.split("!!")

        l = 0
        while l < len(t_ls):
            if t_ls[l].strip("") == "":
                t_ls.pop(l)
                continue

            try:
                if t_ls[l+1].strip("") == "":
                    t_ls.pop(l+1)
                    continue
            except:
                break

            if (t_ls[l].split("---"))[0] == title:
                break
            l += 1
    
        a = user.article.strip("")
        a_ls = a.split("@@")

        q = 0
        while q < len(a_ls):
            if a_ls[q].strip("") == "":
                a_ls.pop(q)
                continue
            q += 1

        a_ls[l] += "##"
        a_ls[l] += comment_user
        a_ls[l] += ": "
        a_ls[l] += comment

        a1 = ""
        for q in a_ls:
            a1 += q
            a1 += "@@"
        
        user.article = a1
        session.delete(user)
        session.add(user)
        print('yes')
        session.commit()



def get_comment(username, title):
    user = get_user(username)
    t = user.title.strip("")
    t_ls = t.split("!!")

    l = 0
    while l < len(t_ls):
        if t_ls[l].strip("") == "":
            t_ls.pop(l)
            continue

        try:
            if t_ls[l+1].strip("") == "":
                t_ls.pop(l+1)
                continue
        except:
            break

        if (t_ls[l].split("---"))[0] == title:
            break
        l += 1
    
    a = user.article.strip("")
    a_ls = a.split("@@")

    q = 0
    while q < len(a_ls):
        if a_ls[q].strip("") == "":
            a_ls.pop(q)
            continue
        q += 1
    
    comment_ls = a_ls[l].split('##')
    comment_ls.pop(0)

    l = 0
    while l < len(comment_ls):
        if comment_ls[l].strip("") == "":
            comment_ls.pop(l)
            continue
        l += 1
    return comment_ls



def Delete_comment(username, title, comment):
    with Session(engine) as session:
        user = get_user(username)
        t = user.title.strip("")
        t_ls = t.split("!!")

        l = 0
        while l < len(t_ls):
            if t_ls[l].strip("") == "":
                t_ls.pop(l)
                continue

            try:
                if t_ls[l+1].strip("") == "":
                    t_ls.pop(l+1)
                    continue
            except:
                break

            if (t_ls[l].split("---"))[0] == title:
                break
            l += 1
    
        a = user.article.strip("")
        a_ls = a.split("@@")

        q = 0
        while q < len(a_ls):
            if a_ls[q].strip("") == "":
                a_ls.pop(q)
                continue
            q += 1

        comment_ls = a_ls[l].split("##")
        
        
        k = 1
        while k < len(comment_ls):
            if comment_ls[k].count(comment) > 0:
                comment_ls.pop(k)
                break
            k += 1
        
        a1 = ""
        for k in comment_ls:
            a1 += k
            a1 += "##"
        
        a_ls[l] = a1.rstrip("##")

        a2 = ""
        for l in a_ls:
            a2 += l
            a2 +='@@'
        
        user.article = a2
        session.delete(user)
        session.add(user)
        session.commit()


def Mute(username):
    with Session(engine) as session:
        user = get_user(username)
        user.mute_status = "TRUE"
        session.delete(user)
        session.add(user)
        session.commit()


def Unmute(username):
    with Session(engine) as session:
        user = get_user(username)
        user.mute_status = "FALSE"
        session.delete(user)
        session.add(user)
        session.commit()

def get_role(username):
    user = get_user(username)
    return user.role

def get_mute_status(username):
    user = get_user(username)
    return user.mute_status

def search_chat(text):
    with Session(engine) as session:
        search_results = session.query(MessageHistory).filter(MessageHistory.message.like(f'%{text}%')).all()
        session.close()
        return [result.message for result in search_results]

