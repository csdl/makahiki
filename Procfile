web: newrelic-admin run-program python makahiki/manage.py run_gunicorn -b 0.0.0.0:$PORT -w 3
#web: newrelic-admin run-program python makahiki/manage.py runserver 0.0.0.0:$PORT
celeryd: python makahiki/manage.py celeryd -E -B --loglevel=INFO
