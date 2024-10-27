# entrypoint.sh
#!/bin/sh

# Run database migrations
echo "Applying database migrations..."
python3 manage.py makemigrations
python3 manage.py migrate

# Start Django server
echo "Starting ClaraXO Django server..."
gunicorn --workers 4 --bind 0.0.0.0:8000 tictactoe_backend.wsgi:application