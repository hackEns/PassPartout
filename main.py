import os
import subprocess
from flask import Flask, render_template_string, render_template, request, redirect
from flask_mail import Mail
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter, roles_required, current_user

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
		print(dir(current_user))
		if request.method == "POST":
			user = db.session.query(User).filter(User.id==request.form["user"]).first()
			role = db.session.query(Role).filter(Role.id==request.form["role"]).first()
			if "val" in request.form and request.form["val"] == "on":
				user.roles.append(role)
			else:
				if role in user.roles:
					user.roles.remove(role)
			db.session.commit()
		return render_template("grid.html", users=db.session.query(User), roles=db.session.query(Role))
	
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

	return app


# Start development web server
if __name__=='__main__':
	app = create_app()
	app.run(host='0.0.0.0', port=5000, debug=False)
