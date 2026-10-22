.PHONY: install lint test format run migrate seed

install:
	pip install -r requirements.txt

lint:
	pylint --load-plugins=pylint_django --django-settings-module=EduTHY.settings \
		--disable=C0103,C0114,C0115,C0301,C0304,E5142,R0903 \
		AIQandA EduTHY || true

test:
	pytest -v

format:
	black .

run:
	python manage.py runserver 0.0.0.0:8000

migrate:
	python manage.py migrate

seed:
	python manage.py seed_data
