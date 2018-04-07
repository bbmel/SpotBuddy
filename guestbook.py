from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from urlparse import urlparse, urljoin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql9230362:bjrNRpqhBj@sql9.freemysqlhosting.net/sql9230362'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Thisisasecret!'
app.config['USE_SESSION_FOR_NEXT'] = True

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))

	return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

class Comments(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))
	comment = db.Column(db.String(1000))

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), unique=True)


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		user = User.query.filter_by(username=username).first()
		if not user:
			return '<h1>User does not exist!</h1>'

		login_user(user)

		if 'next' in session:
			next = session['next']

			if is_safe_url(next) and next is not None:
				return redirect(next)

		return '<h1>You are now logged in!</h1>'

	session['next'] = request.args.get('next')
	return render_template('login.html')

@app.route('/home')
@login_required
def home():
	return '<h1>You are in the protected area, {}!</h1>'.format(current_user.username)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return '<h1>You are now logged out!</h1>'



@app.route('/')
def index():
	result = Comments.query.all()

	return render_template('index.html', result=result)

@app.route('/sign')
def sign():
	return render_template('sign.html')

@app.route('/process', methods=['POST'])
def process():
	name = request.form['name']
	comment = request.form['comment']

	signature = Comments(name=name, comment=comment)
	db.session.add(signature)
	db.session.commit()
	
	return redirect(url_for('index'))

#@app.route('/home', methods=['GET', 'POST'])
#@login_required
#def home():
	#return render_template('example.html')

if __name__ == '__main__':
	app.run(debug=True)