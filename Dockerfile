FROM tiangolo/uwsgi-nginx-flask:python3.5

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

COPY app app
COPY config.py main.py ./
COPY app.db ./

EXPOSE 80
