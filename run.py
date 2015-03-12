#!/usr/bin/python

from passmanager import create_app
import os

# Start development web server
if __name__=='__main__':
	app = create_app()
	debug = os.getenv("DEBUG", False)
	if debug:
		app.run(host='localhost', port=5000, debug=True)
	else:
		app.run(host='0.0.0.0', port=5000)
