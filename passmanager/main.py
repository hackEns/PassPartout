import os
import subprocess
from flask import Flask, render_template_string, render_template, request, redirect
from flask_mail import Mail
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter, roles_required, current_user

from passmanager.utils import id_generator

from passmanager.db import init_db

from wtforms.validators import ValidationError

import sys
import os.path


def install_secret_key(app, filename='secret_key'):
	"""Configure the SECRET_KEY from a file
	in the instance directory.

	If the file does not exist, print instructions
	to create it from a shell with a random key,
	then exit.

	"""
	filename = os.path.join(app.instance_path, filename)
	try:
		app.config['SECRET_KEY'] = str(open(filename, 'rb').read())
	except IOError:
		print('Error: No secret key. Create it with:')
		if not os.path.isdir(os.path.dirname(filename)):
			print('mkdir -p', os.path.dirname(filename))
		print('head -c 24 /dev/urandom >', filename)
		sys.exit(1)

# Use a Class-based config to avoid needing a 2nd file
# os.getenv() enables configuration through OS environment variables
class ConfigClass(object):
	# Flask settings
	CSRF_ENABLED = True

	# Flask-Mail settings
	MAIL_USERNAME =		   os.getenv('MAIL_USERNAME',		'')
	MAIL_PASSWORD =		   os.getenv('MAIL_PASSWORD',		'')
	MAIL_DEFAULT_SENDER =	 os.getenv('MAIL_DEFAULT_SENDER',  '"PassManager" <noreply@hack.ens.fr>')
	MAIL_SERVER =			 os.getenv('MAIL_SERVER',		  'smtp.gmail.com')
	MAIL_PORT =		   int(os.getenv('MAIL_PORT',			'465'))
	MAIL_USE_SSL =		int(os.getenv('MAIL_USE_SSL',		 True))
	USER_ENABLE_CONFIRM_EMAIL = False
	USER_ENABLE_REGISTRATION = False
	USER_ENABLE_EMAIL = False

	CAS_SERVER = "https://cas.eleves.ens.fr/"

	CAS_SERVICE = "http://localhost:5000"

	# Flask-User settings
	USER_APP_NAME		= "PassManager"				# Used by email templates


def create_app():
	""" Flask application factory """

	# Setup Flask app and app.config
	app = Flask(__name__)
	app.config.from_object(__name__+'.ConfigClass')
	app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + app.instance_path + os.sep + "users.sqlite"
	print(app.config['SQLALCHEMY_DATABASE_URI'])
	install_secret_key(app)

	# Initialize Flask extensions
	mail = Mail(app)								# Initialize Flask-Mail

	db, user_db_adapter, User, Role = init_db(app)

	# Setup Flask-User
	def password_validator(form, field):
		password = field.data
		if len(password) < 6:
			raise ValidationError(('Password must have at least 6 characters'))
	
	def username_validator(form, field):
		""" Username must cont at least 3 alphanumeric characters long"""
		username = field.data
		if len(username) < 1:
			raise ValidationError(('Username must be at least 1 characters long'))

	user_manager = UserManager(user_db_adapter, password_validator=password_validator, username_validator=username_validator)
	user_manager.init_app(app) # Initialize Flask-User

	# A flask/sqlalchemy/python bug? anyway sqlalchemy complains in a weird error without this line
	User.query


	# The Home page is accessible to anyone
	@app.route('/')
	@login_required
	def home_page():
		return render_template("index.html", current_user=current_user)

	# The Home page is accessible to anyone
	@app.route('/keyring/<name>')
	@login_required
	def keyring(name):
		found = False
		for r in current_user.roles:
			found = found or r.name == name
		if not found:
			return "Not authorized"
		return render_template("keyring.html", keyring=name)

	@app.route('/grid', methods=["POST", "GET"])
	@login_required
	@roles_required('hacker')
	def grid():
		if request.method == "POST":
			user = db.session.query(User).filter(User.id==request.form["user"]).first()
			role = db.session.query(Role).filter(Role.id==request.form["role"]).first()
			if "val" in request.form and request.form["val"] == "on":
				user.roles.append(role)
			else:
				if role in user.roles:
					user.roles.remove(role)
			db.session.commit()
		return render_template("grid.html", users=db.session.query(User), roles=db.session.query(Role), user_reset_id = "-1", newpass = "")
	
	@app.route('/grid/reset/<user_id>')
	@login_required
	@roles_required('hacker')
	def reset_grid(user_id):
		user = db.session.query(User).filter(User.id==int(user_id)).first()
		newpass = id_generator()
		user.password = user_manager.hash_password(newpass)
		db.session.commit()
		return render_template("grid.html", users=db.session.query(User), roles=db.session.query(Role), newpass=newpass, user_reset_id=user_id)


	@app.route('/new', methods=["POST", "GET"])
	@login_required
	@roles_required('hacker')
	def new():
		if request.method == "POST":
			rolename = request.form["role"]
			if not db.session.query(Role).filter(Role.name==rolename).first():
				new_role = Role(name=rolename)
				db.session.add(new_role)
				current_user.roles.append(new_role)
				db.session.commit()

				save(rolename, True)

				return redirect("/grid")
		return render_template("create.html", users=db.session.query(User), roles=db.session.query(Role))



	@app.route('/save/<name>', methods=["POST"])
	@login_required
	def save(name, initial = False):
		found = False
		for r in current_user.roles:
			found = found or r.name == name
		if not found:
			return "Not authorized"
		if initial:
			if subprocess.call(["touch", name + ".txt"], cwd="db/") != 0:
				print("Keyring already exists??")
				return "error"

		if subprocess.call(["git", "add", name + ".txt"], cwd="db/") != 0:
			print("git error")
			return "error"
		subprocess.call(["git", "commit", "-m", "commit pre-web-update"], cwd="db/")

		with open("db/" + name + ".txt", "w") as f:
			f.write(request.form["data"])
			f.close()
		if subprocess.call(["git", "add", name + ".txt"], cwd="db/") != 0:
			print("git error")
			return "error"
		if subprocess.call(["git", "commit", "-m", "Web update"], cwd="db/") != 0:
			print("git error")
			return "error"
		return "done"

	@app.route('/get/<name>')
	@login_required
	def get(name):
		found = False
		for r in current_user.roles:
			found = found or r.name == name
		if not found:
			return "Not authorized"
		try:
			with open("db/" + name + ".txt", "r") as f:
				return f.read()
		except FileNotFoundError:
			return "{}"

	return app,db, user_db_adapter, User, Role, user_manager


