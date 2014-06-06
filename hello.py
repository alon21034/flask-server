import os
import sqlite3
import random
import urllib, urllib2
from flask import *
from functools import wraps

app = Flask(__name__)

DATABASE = 'test.db'
app.secret_key = 'secret'
app.config.from_object(__name__)

def py_get_public_key(server_info):
	return (hex)((int)(random.getrandbits(128)))

def py_get_device_UUID(nonce):
	return (hex)((int)(random.getrandbits(128)))

def py_get_signed_nonce(nonce):
	return (hex)((int)(random.getrandbits(128)))

@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
	error = None

	if request.method == 'POST':
		if check_in_db(request.form['username'], request.form['password']):
			session['logged_in'] = True
			return redirect(url_for('hello'))
		else:
			error = 'Invalid credentials, try again!'

	return render_template('index.html', error=error)

def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash('You need to log in first!')
			return redirect(url_for('index'))
	return wrap

@app.route('/hello')
@login_required
def hello():
	return render_template('welcome.html')

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out.')
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		
		return redirect(url_for('index'))

	return render_template('register.html')

@app.route('/test')
def test():
	g.db = connect_db()
	cur = g.db.execute('select * from USER')
	return cur.fetchall()[0][0]

@app.route('/get_public_key')
def web_get_public_key():
	print 'get_public_key'

	return redirect("http://localhost:5000/reader_get_public_key?return_to=%s" % request.host)

@app.route('/reader_get_public_key', methods=['GET'])
def reader_get_public_key():
	print 'reader_get_public_key'

	remote = request.args.get('return_to')
	print remote
	url = request.args.get('http://%s/' % remote)
	public_key=py_get_public_key(url)
	data = {'public_key':public_key, 'username':'admin', 'password':'admin'}
	return post(url, data)

@app.route('/test_urllib')
def test_urllib():
	return post('http://nfc-auth-solution.herokuapp.com/', {'username':'admin', 'password':'admin'})

def post(url, data):  
    req = urllib2.Request(url)  
    data = urllib.urlencode(data)  
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())  
    response = opener.open(req, data)  
    return response.read()  

def save_in_db(username, password):
	g.db = connect_db()
	cur = g.db.execute("insert into USER values('%s','%s')" % (username, password))
	g.db.commit()
	g.db.close()

def check_in_db(username, password):
	g.db = connect_db()
	cur = g.db.execute("select * from USER where username='%s' and password='%s'" %(username,password))
	res = cur.fetchall()

	if len(res) == 0:
		return False
	else:
		return True

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

if __name__ == '__main__':
	app.run(port = 5000, debug=True)
