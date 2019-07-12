import os
from flask import Flask, request, redirect, url_for,render_template
from werkzeug import secure_filename
import IPython
import json
import time
from tqdm import tqdm
from shengdao import ShengdaoClient
from flask import g  

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask('my web')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = '1234231'



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

@app.route('/upload_file', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		# IPython.embed()
		BASE_DIR = os.path.dirname(__file__)
		# mkdir_file(os.path.join(BASE_DIR, 'file/img/xiao'))
		f = request.files.get('file')
		filename = f.filename
		if filename.split('.')[-1] == 'txt':
			f.save(os.path.join(BASE_DIR, filename))
			file_path = os.path.join(BASE_DIR, filename)
			datas = file_processing(file_path)
			return render_template('server.html',datas=datas,numbers=len(datas),file_name=filename)
		else:
			return json.dumps({'error':'文件不是txt格式'})
	else:
		return json.dumps({'code':405,'error':'请求方式不正确'})

@app.route('/index/',methods=['GET','POST'])
def index():
	return render_template('index.html')

@app.route('/getbar/<filename>',methods=['GET','POST'])
def getbar(filename):
	file = open(filename+'bar.txt','r+')
	try:
		lines = file.readlines()
	except:
		file = open(filename+'bar.txt','w+')
		return 
	bar = lines[-1:][0]
	return bar

@app.route('/search_regist/<filename>',methods=['GET','POST'])
def search_regist(filename):
	datas = file_processing(filename)
	f = open(filename+'_search_regist', "w+")
	for data in tqdm(datas,file=open(filename+'bar.txt','w+'),ncols=80):
		client = ShengdaoClient(data[1],data[2],data[0])
		shoes = client.search_register()
		for shoe in shoes:
			f.write(''.join([data[0],shoe['itemName'],shoe['shopName'],shoe['state'],'\n']))
			f.flush()

@app.route('/search_result/<filename>',methods=['GET','POST'])
def search_result(filename):
	f = open(filename+'_search_regist', "r+")
	return render_template('search_result.html',datas=f.readlines())


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
