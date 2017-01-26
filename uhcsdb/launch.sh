BOKEH_LOG_LEVEL=debug bokeh serve --port 8001 --host=rsfern.materials.cmu.edu --allow-websocket-origin=uhcsdb.materials.cmu.edu --log-level=debug visualize.py

gunicorn uhcsdb:app


