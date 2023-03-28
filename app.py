from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
import hashlib
from datetime import datetime, timedelta
import certifi
from datetime import datetime

SECRET_KEY = 'secret_key'


client = MongoClient('mongodb+srv://sparta:test@cluster0.icwksk1.mongodb.net/?retryWrites=true&w=majority' ,tlsCAFile=certifi.where())
db = client.dbsparta
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():

    id_receive = request.form['id_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    username_receive = request.form['username_give']
    userbirth_receive = request.form['userbirth_give']
    userphone_receive = request.form['userphone_give']
    userEmail_receive = request.form['userEmail_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest() # password 해쉬화 함수
    doc = {
        "id": id_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "nickname": nickname_receive,  # 닉네임
        "username": username_receive,  # 닉네임
        "userbirth": userbirth_receive,  # 닉네임
        "userphone": userphone_receive,  # 닉네임
        "userEmail": userEmail_receive,  # 닉네임
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
    result = db.users.find_one({'id': username_receive, 'password': pw_hash}) 
    # 아이디와 유저가 입력한 해쉬화된 pw가 DB에 저장되어 있는 해쉬화된 pw와 일치하는지 확인 

    if  result['id'] == username_receive:  # 일치한다면
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 1)  # 로그인 1시간 유지
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
    
@app.route('/board')
@jwt_required()
def board():
    current_user = get_jwt_identity()
    return render_template('board.html', current_user=current_user)
    
@app.route("/board/show", methods=["GET"])
def board_get():
    all_content = list(db.board.find({},{'_id':False}))
    return jsonify({'result':all_content})

@app.route("/board/save", methods=["POST"])
def save_post():
    token_receive = request.cookies.get('mytoken')
    title_receive = request.form["title_give"]
    content_receive = request.form["content_give"]
    now = str(datetime.now().date())

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        doc = {
            'title': title_receive,
            'content': content_receive,
            'id': payload['id'],
            'date': now
        }
        db.board.insert_one(doc)


        return jsonify({'msg':'작성 완료!'})
    except jwt.ExpiredSignatureError:
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        return render_template('index.html')


# 이부분이 동작하게 되는데
# cookie에 저장되어있는 token값을 꺼낸뒤에 token_receive에 저장합니다
# 그리고 payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256']) 이
# 부분에서 token값을 다시 id값으로 바꿔줍니다 
# 이때 만약 만료된 토큰이거나 가지고 있는 토큰이 문제가 있다면
# 다시 버튼이 있는 페이지로 redirect시켜줍니다.

@app.route('/simplelogin2')
def home2():
	token_receive = request.cookies.get('mytoken')
        
	try:
		payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
		print(payload)
		return render_template('index2.html')
	except jwt.ExpiredSignatureError:
		return render_template('index.html')
	except jwt.exceptions.DecodeError:
		return render_template('index.html')

@app.route('/index')
def login():
    return render_template('simplelogin.html')

@app.route('/index2')
def login_index():
    return render_template('index2.html')

@app.route('/login_sign_up')
def login_sign_up():
    return render_template('10_jo_blog_join_the_membership.html')

@app.route("/post", methods=["GET"])
def post_get():
    token_receive = request.cookies.get('mytoken')
        
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        posts = list(db.board.find({'id': payload['id']},{'_id':False}))
        return jsonify({'result':posts})
    except jwt.ExpiredSignatureError:
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)