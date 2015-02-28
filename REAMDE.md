PassManager
-----------

A webapp written in python, with flask to store password.

The passwords are stored in an encrypted JSON file on the server.

The encryption is only done client side, using AES in javascript. When a user adds a password or edit one, the JSON file si crypted and then sent to the server, who saves it. Everything is archived using git, so as it can be restored at any point.


Features
--------
* Client side encryption
* Multiple keyring
* User accounts, UI to manage the permission of every user (administration, which keyrings one can access, etc…)
* History using git
* Support both python2/python3 if the appropriate modules are installed


Install
-------
Run "install_modules.sh" to install the required python modules and setup the git repository used for the keyrings.

Then run "python run.py"
