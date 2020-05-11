#!bin/bash
pip install -r requirements.txt
python manage.py makemigrations --noinput
python manage.py makemigrations api --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py shell -c "import runpy; runpy.run_path('/backend/create-s-user.py');"
python manage.py runserver 0.0.0.0:8000 --insecure

# uvicorn backend.asgi:application --host 0.0.0.0

