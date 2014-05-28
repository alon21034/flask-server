import os
from flask import *
from functools import wraps

app = Flask(__name__, static_url_path='')

app.secret_key = 'secret'

@app.route('/index')
@app.route('/', methods=['GET', 'POST'])
def index():
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid credentials, try again!'
		else:
			session['logged_in'] = True
			return redirect(url_for('hello'))

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

if __name__ == '__main__':
	app.run(debug=True)
