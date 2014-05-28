import os
from flask import *

app = Flask(__name__, static_url_path='')

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/login')
def login():
	return 'Login'

if __name__ == '__main__':
	app.run()
