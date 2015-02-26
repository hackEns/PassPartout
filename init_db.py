#!/usr/bin/env python

from db import init_db
from flask import Flask
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
import main

app = Flask("main")
app.config.from_object(main.ConfigClass)

db, user_db_adapter, User, Role = init_db(app)
user_manager = UserManager(user_db_adapter, app)	 # Initialize Flask-User

user = User(username='root', active=True,
	password=user_manager.hash_password('root'))
hacker = Role(name='hacker')
user.roles.append(hacker)

db.session.add(user)
db.session.add(hacker)
db.session.commit()
