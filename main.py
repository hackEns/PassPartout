import os
from flask import Flask, render_template_string, render_template, request
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter


# Use a Class-based config to avoid needing a 2nd file
# os.getenv() enables configuration through OS environment variables
class ConfigClass(object):
	# Flask settings
	SECRET_KEY =			  os.getenv('SECRET_KEY',	   'THIS IS AN INSECURE SECRET')
	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',	 'sqlite:///basic_app.sqlite')
	CSRF_ENABLED = True

	# Flask-Mail settings
	MAIL_USERNAME =		   os.getenv('MAIL_USERNAME',		'')
	MAIL_PASSWORD =		   os.getenv('MAIL_PASSWORD',		'')
	MAIL_DEFAULT_SENDER =	 os.getenv('MAIL_DEFAULT_SENDER',  '"MyApp" <noreply@example.com>')
	MAIL_SERVER =			 os.getenv('MAIL_SERVER',		  'smtp.gmail.com')
	MAIL_PORT =		   int(os.getenv('MAIL_PORT',			'465'))
	MAIL_USE_SSL =		int(os.getenv('MAIL_USE_SSL',		 True))
	USER_ENABLE_CONFIRM_EMAIL = False
	USER_ENABLE_REGISTRATION = True

	# Flask-User settings
	USER_APP_NAME		= "Appppp"				# Used by email templates


def create_app():
	""" Flask application factory """
	
	# Setup Flask app and app.config
	app = Flask(__name__)
	app.config.from_object(__name__+'.ConfigClass')

	# Initialize Flask extensions
	db = SQLAlchemy(app)							# Initialize Flask-SQLAlchemy
	mail = Mail(app)								# Initialize Flask-Mail

	# Define the User data model. Make sure to add flask.ext.user UserMixin !!!
	class User(db.Model, UserMixin):
		id = db.Column(db.Integer, primary_key=True)

		# User authentication information
		username = db.Column(db.String(50), nullable=False, unique=True)
		password = db.Column(db.String(255), nullable=False, server_default='')
		reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

		# User email information
		email = db.Column(db.String(255), nullable=False, unique=True)
		confirmed_at = db.Column(db.DateTime())

		# User information
		active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
		first_name = db.Column(db.String(100), nullable=False, server_default='')
		last_name = db.Column(db.String(100), nullable=False, server_default='')

	# Create all database tables
	db.create_all()

	# Setup Flask-User
	db_adapter = SQLAlchemyAdapter(db, User)		# Register the User model
	user_manager = UserManager(db_adapter, app)	 # Initialize Flask-User

	# The Home page is accessible to anyone
	@app.route('/')
	@login_required
	def home_page():
		return render_template("index.html")
		"""
			{% extends "base.html" %}
			{% block content %}
				<h2>Home page</h2>
				<p>This page can be accessed by anyone.</p><br/>
				<p><a href={{ url_for('home_page') }}>Home page</a> (anyone)</p>
				<p><a href={{ url_for('members_page') }}>Members page</a> (login required)</p>
			{% endblock %}
			"""

	# The Members page is only accessible to authenticated users
	@app.route('/pass')
	@login_required								 # Use of @login_required decorator
	def members_page():
		return render_template_string("""
			{% extends "base.html" %}
			{% block content %}
				<h2>Members page</h2>
				<p>This page can only be accessed by authenticated users.</p><br/>
				<p><a href={{ url_for('home_page') }}>Home page</a> (anyone)</p>
				<p><a href={{ url_for('members_page') }}>Members page</a> (login required)</p>
			{% endblock %}
			""")
	
	@app.route('/save', methods=["POST"])
	@login_required
	def save():
		if subprocess.call(["git", "add", "db.txt"], cwd="db/") != 0:
			print("git error")
			return "error"
		subprocess.call(["git", "commit", "-m", "commit pre-web-update"], cwd="db/")

		with open("db/db.txt", "w") as f:
			f.write(request.form["data"])
			f.close()
		if subprocess.call(["git", "add", "db.txt"], cwd="db/") != 0:
			print("git error")
			return "error"
		if subprocess.call(["git", "commit", "-m", "Web update"], cwd="db/") != 0:
			print("git error")
			return "error"
		return "done"
	
	@app.route('/get')
	@login_required
	def get():
		with open("db/db.txt", "r") as f:
			return f.read()

	return app


# Start development web server
if __name__=='__main__':
	app = create_app()
	app.run(host='localhost', port=5000, debug=True)
