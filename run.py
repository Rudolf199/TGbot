import subprocess
import sys
import os

subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
print("Your bot token please: ")
os.environ['bottoken'] = input()
print("Your database host: ")
os.environ['dbhost'] = input()
print("Your db password: ")
os.environ['password'] = input()
print("Your db port: ")
os.environ['port'] = input()
print("Your db user: ")
os.environ['user'] = input()
print("your database: ")
os.environ['database'] = input()
print("Your channel url: ")
os.environ['channel'] = input()
subprocess.call(['python', 'app.py'])
