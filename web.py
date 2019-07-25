import os
from flask import Flask, request, redirect, url_for,render_template,session
from werkzeug import secure_filename
import IPython
import json
import time
from tqdm import tqdm
from shengdao import ShengdaoClient
from flask import g  

Usernames = ['chenshaowen']
passwords = {'chenshaowen':'123456'}

app = Flask('my web')

app.config['SECRET_KEY'] = '1234231'

from flask_wtf import FlaskForm as Form 
from wtforms import StringField, PasswordField 
from wtforms.validators import DataRequired 
  
# 会员登录日志
# class Userlog(db.Model):
#     __tablename__ = "userlog"
#     id = db.Column(db.Integer, primary_key=True)  # 编号
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员
#     ip = db.Column(db.String(100))  # 登录IP
#     addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 登录时间

#     def __repr__(self):
#         return "<Userlog %r>" % self.id
   
class LoginForm(Form): 
    Username = StringField('Username', validators=[DataRequired('Username is null')]) 
    password = PasswordField('password', validators=[DataRequired('password is null')]) 

def file_processing(file_path):
	shengdaolist = []
	try:
		for line in open(file_path):
			if '已知信息' in line:
				break
			items = line.strip().split(' ')
			shengdaolist.append([items[0],items[1],items[2]])
		return shengdaolist
	except:
		return '='*50+'此行格式错误'+'='*50 + '\n' + line


@app.route('/get_files', methods=['POST'])
def get_files():
	if request.method == 'POST':
		files = []
		path = session['path']
		for file in os.listdir(path):
			if os.path.isfile(os.path.join(path,file)) and 'txt' in file:
				files.append(file)
		return json.dumps(files)

@app.route('/upload_file', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		Username = session['Username']
		path = session['path']
		if not os.path.isdir(path):
			os.mkdir(path)
			os.mkdir(os.path.join(path,'result'))
		f = request.files.get('file')
		filename = f.filename
		if filename.split('.')[-1] == 'txt':
			f.save(os.path.join(path, filename))
			return render_template('index.html',Username=Username)
		else:
			return json.dumps({'error':'文件不是txt格式'})
	else:
		return json.dumps({'code':405,'error':'请求方式不正确'})

@app.route('/login/',methods=['GET','POST'])
def login():
	form = LoginForm()
	status = ''
	if 'status' in request.args.to_dict():
		status = request.args.to_dict()['status']
	return render_template('login.html',form=form,status=status)	

@app.route('/index',methods=['GET','POST'])
def index():
	Username = request.form.to_dict()['Username']
	pwd = request.form.to_dict()['password']
	if Username in Usernames and pwd == passwords[Username]:
		session['Username'] = Username
		BASE_DIR = os.path.dirname(__file__)
		path = os.path.join(BASE_DIR, session['Username'])
		session['path'] = path
		return render_template('index.html',Username=Username)
	else:
		return redirect(url_for('login',status="账号密码错误"))
	# request.form.

@app.route('/server/<file>',methods=['GET','POST'])
def server(file):	
	file_path = os.path.join(session['path'],file)
	datas = file_processing(file_path)
	return render_template('server.html',datas=datas,numbers=len(datas),file_name=file)

@app.route('/getbar/<filename>',methods=['GET','POST'])
def getbar(filename):
	bar_path = os.path.join(session['path'],'result',filename+'bar.txt')
	file = open(bar_path,'r+')
	try:	
		lines = file.readlines()
	except:
		file = open(bar_path,'w+')
		return 
	bar = lines[-1:][0]
	return bar

@app.route('/search_regist/<filename>',methods=['GET','POST'])
def search_regist(filename):
	datas = file_processing(os.path.join(session['path'],filename))
	bar_path = os.path.join(session['path'],'result',filename+'bar.txt')
	f = open(os.path.join(session['path'],'result',filename+'_regist_regist.txt'), "w+")
	for data in tqdm(datas,file=open(bar_path,'w+'),ncols=80):
		client = ShengdaoClient(data[1],data[2],data[0],'')
		shoes = client.search_register()
		for shoe in shoes:
			f.write(''.join([data[0],shoe['itemName'],shoe['shopName'],shoe['state'],'\n']))
			f.flush()

@app.route('/regist_result/<filename>',methods=['GET','POST'])
def regist_result(filename):
	f = open(os.path.join(session['path'],'result',filename+'_regist_regist.txt'), "r+")
	return render_template('search_result.html',datas=f.readlines())

@app.route('/lucky_result/<filename>',methods=['GET','POST'])
def lucky_result(filename):
	f = open(os.path.join(session['path'],'result',filename+'_regist_regist.txt'), "r+")
	lines = []
	for line in f.readlines():
		if '中签' in line:
			lines.append(line)
	return render_template('search_result.html',datas=lines)

if __name__ == '__main__':
	# parser = argparse.ArgumentParser()
	# parser.add_argument('data_source', type=str)
	# parser.add_argument('--bind', default='0.0.0.0', type=str)
	# parser.add_argument('--port', default=8866, type=int)
	# parser.add_argument('--handler', type=str)
	# args = parser.parse_args()


	# CURR_DIR = args.data_source
	# CURR_DIR = os.path.abspath(CURR_DIR)
	# hint_url(args.port)
	# app.run(args.bind, args.port, threaded=True)	
	app.run(host='0.0.0.0',port=5000,debug=True)
