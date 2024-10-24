superuser:
	python3 manage.py createsuperuser

collectstatic:
	python3 manage.py collectstatic

test:
	pytest

clean:
	rm db.sqlite3

install:
	pip install -r requirements.txt

all: migrate run

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

run:
	python3 manage.py runserver 0.0.0.0:8000

killserver:
	sudo killall gunicorn

gunicorn:
	gunicorn --workers 3 --bind 0.0.0.0:8000 tictactoe_backend.wsgi:application &

lsof:
	sudo lsof -i :8000

checksyntax:
	sudo nginx -t

nginx:
	sudo systemctl restart nginx