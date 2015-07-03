pip install -r requirements.txt --user
mkdir -p instance
head -c 24 /dev/urandom > instance/secret_key
python init_db.py
