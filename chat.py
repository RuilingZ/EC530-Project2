import json
import os
import base64
import time
import device_module as dev
import pymongo
from flask import Flask, make_response

app = Flask(__name__)

db = './ec530_p2.db'
test_img = 'test.PNG'
media_history = './history/'

@app.route('/chat_module')
def initial_chat_module():
    return dev.init_dataset()

def exist_db_check(end1, end2):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    dblist = myclient.list_database_names()
    if f"chat_record_{end2}_{end1}" in dblist:
        return f"chat_record_{end2}_{end1}"
    else:
        return f"chat_record_{end1}_{end2}"

@app.route('/chat_module/<int:end1>_<int:end2>')
def create_chat(end1, end2):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_name = exist_db_check(end1, end2)
    chat_record = myclient[db_name]
    medical_record = chat_record["medical_record"]
    x = medical_record.delete_many({})
    
    conn = dev.create_connection(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM device_assignment where Responsible_Person = ? AND Assign_to = ?", (end1, end2))
    rows = cur.fetchall()
    respp = dev.select_user(conn, end1)
    assto = dev.select_user(conn,end2)
    
    for row in rows:
        cur.execute("SELECT * FROM record where Assignment = ?", (row[0],))
        records = cur.fetchall()
        cur.execute("SELECT * FROM devices where D_ID = ?", (row[3],))
        device = cur.fetchall()
        for record in records:
            try:
                info = {"R_ID": record[0], "Responsible_Person": respp[1], "Assign_to": assto[1], "Device": device[0][2], "Record_time": record[2], "Value": record[3]}
            except Exception as e:
                print(e)
            medical_record.insert_one(info)
    return print_medical_history(end1, end2)

@app.route('/chat_module/<int:end1>_<int:end2>/media/upload_<media_name>')
def send_media(end1, end2, media_name):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_name = exist_db_check(end1, end2)
    chat_record = myclient[db_name]
    media_record = chat_record["media_record"]
    chat_history = chat_record["chat_record"]
    date = time.strftime("%Y-%m-%d", time.localtime())
    now = time.strftime("%H:%M:%S", time.localtime())
    media_record.delete_many({"Name": media_name})

    with open('./' + media_name, 'rb') as f:
        img_byte = base64.b64encode(f.read())
    f.close()
    img_str = img_byte.decode('ascii')

    media = {"Name": media_name, "Image": img_str}
    info = {"From": end1, "To": end2, "Date": date, "Time": now, "Message_Type": "image", "Message": media_name}
    media_record.insert_one(media)
    chat_history.insert_one(info)
    return f"Media {media_name} uploaded successed"

@app.route('/chat_module/<int:end1>_<int:end2>/media/read_<media_name>')
def read_media(end1, end2, media_name):
    if not os.path.exists(media_history):
        os.mkdir(media_history)
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_name = exist_db_check(end1, end2)
    chat_record = myclient[db_name]
    media_record = chat_record["media_record"]
    for media in media_record.find({"Name": media_name}):
        img_str = media["Image"].encode('ascii')
        img_byte = base64.b64decode(img_str)
        with open(media_history + media_name, 'wb') as f:
            f.write(img_byte)
        f.close()
        response = make_response(img_byte)
        response.headers['Content-Type'] = 'image/png'
        return response
    
@app.route('/chat_module/<int:end1>_<int:end2>/chat/<text>')
def insert_chat_record(end1, end2, text):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_name = exist_db_check(end1, end2)
    chat_record = myclient[db_name]
    chat_history = chat_record["chat_record"]
    date = time.strftime("%Y-%m-%d", time.localtime())
    now = time.strftime("%H:%M:%S", time.localtime())
    info = {"From": end1, "To": end2, "Date": date, "Time": now, "Message": text}
    x = chat_history.insert_one(info)
    return print_chat_history(end1, end2)

@app.route('/chat_module/<int:end1>_<int:end2>/media')
def print_media_history(end1, end2):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_name = exist_db_check(end1, end2)
    chat_record = myclient[db_name]
    media_record = chat_record["media_record"]
    history = dict()
    num = 0
    for information in media_history.find({"Name": 1}, {"_id": 0}):
        num += 1
        history[f"media_record_{num}"] = information
    return history

@app.route('/chat_module/<int:end1>_<int:end2>/medical')
def print_medical_history(end1, end2):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_name = exist_db_check(end1, end2)
    chat_record = myclient[db_name]
    medical_record = chat_record["medical_record"]
    history = dict()
    num = 0
    for information in medical_record.find({}, {"_id": 0}):
        num += 1
        history[f"medical_record_{num}"] = information
    return history

@app.route('/chat_module/<int:end1>_<int:end2>/chat')
def print_chat_history(end1, end2):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_name = exist_db_check(end1, end2)
    chat_record = myclient[db_name]
    chat_history = chat_record["chat_record"]
    history = dict()
    num = 0
    for information in chat_history.find({}, {"_id": 0}):
        num += 1
        history[f"chat_record_{num}"] = information
    return history

@app.route('/chat_module/<int:end1>_<int:end2>/chat/clean')
def clean_chat_history(end1, end2):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_name = exist_db_check(end1, end2)
    chat_record = myclient[db_name]
    chat_history = chat_record["chat_record"]
    chat_history.delete_many({})
    return print_chat_history(end1, end2)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True)
    '''
    initial_chat_module()
    create_chat(2, 4)
    send_media(2, 4, test_img)
    read_media(2, 4, test_img)
    clean_chat_history(2, 4)
    insert_chat_record(2, 4, "Hello")
    insert_chat_record(4, 2, "Hello")
    insert_chat_record(2, 4, "Bye")
    insert_chat_record(4, 2, "Bye")
    print_chat_history(2, 4)
    '''