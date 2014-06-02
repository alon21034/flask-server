import os
import sqlite3
import random
import urllib2
from flask import *
from functools import wraps

app = Flask(__name__)

DATABASE = 'test.db'
app.secret_key = 'secret'
app.config.from_object(__name__)

def get_public_key():
	return (hex)((int)(random.getrandbits(128)))

def get_device_UUID():
	return (hex)((int)(random.getrandbits(128)))

def get_signature():
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
		g.db = connect_db()
		cur = g.db.execute("insert into USER values('%s','%s')" % (username, password))
		g.db.commit()
		g.db.close()
		return redirect(url_for('index'))

	return render_template('register.html')

@app.route('/test')
def test():
	g.db = connect_db()
	cur = g.db.execute('select * from USER')
	return cur.fetchall()[0][0]

@app.route('/get_public_key')
def web_get_public_key():
	return urllib2.urlopen("http://140.112.24.8:5001/").read();

@app.route('/reader_get_public_key', methods=['GET'])
def reader_get_public_key():
	return jsonify(public_key=get_public_key())

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
	app.run(debug=True)
