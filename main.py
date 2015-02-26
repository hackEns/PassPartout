import os
import subprocess
from flask import Flask, render_template_string, render_template, request
from flask_mail import Mail
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter, roles_required

from db import init_db

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
	MAIL_DEFAULT_SENDER =	 os.getenv('MAIL_DEFAULT_SENDER',  '"PassManager" <noreply@hack.ens.fr>')
	MAIL_SERVER =			 os.getenv('MAIL_SERVER',		  'smtp.gmail.com')
	MAIL_PORT =		   int(os.getenv('MAIL_PORT',			'465'))
	MAIL_USE_SSL =		int(os.getenv('MAIL_USE_SSL',		 True))
	USER_ENABLE_CONFIRM_EMAIL = False
	USER_ENABLE_REGISTRATION = True
	USER_ENABLE_EMAIL = False

	# Flask-User settings
	USER_APP_NAME		= "PassManager"				# Used by email templates


def create_app():
	""" Flask application factory """
	
	# Setup Flask app and app.config
	app = Flask(__name__)
	app.config.from_object(__name__+'.ConfigClass')

	# Initialize Flask extensions
	mail = Mail(app)								# Initialize Flask-Mail

	db, user_db_adapter, User, Role = init_db(app)

	# Setup Flask-User
	user_manager = UserManager(user_db_adapter, app)	 # Initialize Flask-User

	# A flask/sqlalchemy/python bug? anyway sqlalchemy complains in a weird error without this line
	User.query


	# The Home page is accessible to anyone
	@app.route('/')
	@login_required
	def home_page():
		return render_template("index.html")
	
	@app.route('/grid', methods=["POST"])
	@login_required
	@roles_required('admin')
	def grid():
		return ""
	

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
