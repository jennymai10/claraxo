qcluster:
	python3 manage.py qcluster

check:
	python3 manage.py check

superuser:
	python3 manage.py createsuperuser

collectstatic:
	python3 manage.py collectstatic

test:
	python3 manage.py test

count_lines:
	python3 count_lines.py

heroku_log:
	heroku logs --tail --app c-lara

backup_db:
	cp db.sqlite3 db.sqlite3.bkp

restore_db:
	cp db.sqlite3.bkp db.sqlite3 

test_game:
	python3 ../test_game.py

clean:
	rm /Users/jennymai/Desktop/it_proj/clara_tictactoe/tictactoe_project/db.sqlite3

install:
	pip install -r requirements.txt

all: migrate run

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

run:
	python3 manage.py runserver 0.0.0.0:8000