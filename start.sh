source /home/pi/Documents/SmartReef/virtual/bin/activate
gunicorn --workers 5 --bind 0.0.0.0:8000  -m 007 __init__:app
deactivate
