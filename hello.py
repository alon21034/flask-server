import os
import sqlite3
import random
import urllib, urllib2
import subprocess
import time
from flask import *
from functools import wraps


app = Flask(__name__)

DATABASE = 'test.db'
app.secret_key = 'secret'
app.config.from_object(__name__)

def py_smart_register(nonce):
	print 'py_smart_register'
	print nonce
	public_key = py_get_public_key(nonce)

	time.sleep(1)
	uuid = py_get_device_UUID()
	return public_key, uuid

def parsePublicKey(key):
	return key.encode('utf-8')

def parseUUID(uuid):
	return uuid.encode('utf-8')

def py_smart_login(nonce):
	return py_get_device_UUID(), py_get_signed_nonce(nonce)

def py_get_public_key(nonce):
	public_key = getCommands(["./get-signature", "%s%s" % ('aaaa', nonce)])
	public_key = public_key[2:-1].replace(" ","")
	return public_key

def py_get_device_UUID():
	uuid = getCommands(["./get-signature", "%s" % 'bbbb']) 
	uuid = uuid[2:-1].replace(" ","")
	return uuid

def py_get_signed_nonce(nonce):
	return (hex)((int)(random.getrandbits(128)))

def getCommands(command):
  lines = ""
  output = ""
  print command
  solver = subprocess.Popen(
      command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  
  output += solver.communicate(lines)[0]
  while solver.poll():
		output += solver.communicate()[0]
  print output
  return output

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

	data = {}
	if request.args.get('public_key'):
		data['public'] = request.args.get('public_key').encode('utf-8')

	if request.args.get('uuid'):
		data['uuid'] = request.args.get('uuid').encode('utf-8')

	if request.args.get('signed_nonce'):
		data['signed_nonce'] = request.args.get('signed_nonce').encode('utf-8')

	if data != {}:
		flash(data)
		return redirect(url_for('index'))
	else:
		public_key = None
		uuid = None
		signed_nonce = None
	
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
		save_in_db(username, password)
		return redirect(url_for('index'))

	return render_template('register.html')

@app.route('/test')
def test():
	g.db = connect_db()
	cur = g.db.execute('select * from USER')
	return cur.fetchall()[0][0]

@app.route('/smart_register')
def smart_register():
	return redirect("http://localhost:5000/reader_smart_register?return_to=%s" % request.host)

@app.route('/smart_login')
def smart_login():
	return redirect("http://localhost:5000/reader_smart_login?return_to=%s" % request.host)

@app.route('/get_public_key')
def web_get_public_key():
	print 'get_public_key'
	return redirect("http://localhost:5000/reader_smart_register?return_to=%s" % request.host)

@app.route('/reader_smart_register', methods=['GET'])
def reader_get_public_key():
	print 'reader_smart_register'

	remote = request.args.get('return_to')
	print remote
	url = 'http://%s/' % remote
	a = ""
	l = [hex(ord(c)) for c in url]
	for c in l:
		a += c[2]
		a += c[3]
	public_key, uuid = py_smart_register(a)
	data = {'public_key':public_key, 'uuid':uuid}
	print data
	para = urllib.urlencode(data)
	return redirect("%s?%s" % (url, para))

@app.route('/reader_smart_login', methods=['GET'])
def reader_get_signed_nonce():
	print 'reader_smart_login'

	remote = request.args.get('return_to')
	print remote
	url = 'http://%s/' % remote
	uuid, signed_nonce = py_smart_login(url)
	data = {'uuid':uuid, 'signed_nonce':signed_nonce}
	print data
	para = urllib.urlencode(data)
	return redirect("%s?%s" % (url, para))

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
