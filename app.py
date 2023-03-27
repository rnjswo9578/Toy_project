from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import jwt
import hashlib
from datetime import datetime, timedelta

SECRET_KEY = 'secret_key'


client = MongoClient('mongodb+srv://sparta:test@cluster0.icwksk1.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest() # password 해쉬화 함수
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "nickname": nickname_receive,  # 닉네임
    }
    db.users.insert_one(doc) # 유저가 입력한 아이디 pw 닉네임을 DB에 저장
    return jsonify({'result': 'success'})


# 로그인서버
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']  # 유저가 아이디 pw 입력

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()  # 유저가 입력한 pw를 해쉬화
    result = db.users.find_one({'username': username_receive, 'password': pw_hash}) 
    # 아이디와 유저가 입력한 해쉬화된 pw가 DB에 저장되어 있는 해쉬화된 pw와 일치하는지 확인 

    if result is not None:  # 일치한다면
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        } 
        # 유저 아이디와 유효기간을 담고 있는 payload 생성
        
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256') 
        # jwt기반 토큰 생성

        return jsonify({'result': 'success', 'token': token}) 
        # 토큰을 유저에게 부여
        
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
    

@app.route('/simplelogin')
def simplelogin():
    return render_template('simplelogin.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)