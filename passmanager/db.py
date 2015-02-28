from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin, SQLAlchemyAdapter

def init_db(app):
	db = SQLAlchemy(app)							# Initialize Flask-SQLAlchemy

	# Define Role model
	class Role(db.Model):
		id = db.Column(db.Integer(), primary_key=True)
		name = db.Column(db.String(50), unique=True)

	# Define the User data model. Make sure to add flask.ext.user UserMixin !!!
	class User(db.Model, UserMixin):
		id = db.Column(db.Integer, primary_key=True)

		# User authentication information
		username = db.Column(db.String(50), nullable=False, unique=True)
		password = db.Column(db.String(255), nullable=False, server_default='')
		reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

		# User email information
		email = db.Column(db.String(255), nullable=True, unique=True)
		confirmed_at = db.Column(db.DateTime())

		# User information
		active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
		first_name = db.Column(db.String(100), nullable=False, server_default='')
		last_name = db.Column(db.String(100), nullable=False, server_default='')

		roles = db.relationship('Role', secondary='user_roles')
		# FIXME: really not good performance wise
		def is_admin(self):
			for r in self.roles:
				if r.name == "hacker":
					return True
			return False


	# Define UserRoles model
	class UserRoles(db.Model):
		id = db.Column(db.Integer(), primary_key=True)
		user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
		role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


	# Create all database tables
	db.create_all()
	
	user_db_adapter = SQLAlchemyAdapter(db, User)		# Register the User model

	return db, user_db_adapter, User, Role
