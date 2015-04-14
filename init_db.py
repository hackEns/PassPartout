#!/usr/bin/env python

from passmanager import init_db
from flask import Flask
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from passmanager import main
import os
import subprocess


if not os.path.isdir("db"):
    os.mkdir("db")
    os.chdir("db")
    subprocess.check_call(["git", "init", "."])
    os.chdir("..")

app,db, user_db_adapter, User, Role, user_manager = main.create_app()


user = User(username='root', active=True,
	password=user_manager.hash_password('root'))
hacker = Role(name='hacker')
user.roles.append(hacker)

db.session.add(hacker)
db.session.add(user)
db.session.commit()
