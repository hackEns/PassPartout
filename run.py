#!/usr/bin/python

from passmanager import create_app

# Start development web server
if __name__=='__main__':
	app = create_app()
	app.run(host='0.0.0.0', port=5000, debug=False)
