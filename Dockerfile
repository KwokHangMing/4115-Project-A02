FROM python:3.11.2-alpine
RUN adduser -D microblog

WORKDIR /home/microblog

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN apk add --no-cache --update gcc musl-dev libffi-dev openssl-dev
RUN python3 -m venv venv
RUN venv/bin/pip3 install --upgrade pip 
RUN venv/bin/pip3 uninstall numpy
RUN venv/bin/pip3 freeze > requirements.txt 
RUN venv/bin/pip3 install -r requirements.txt && venv/bin/pip3 install gunicorn

COPY app app
COPY migrations migrations
COPY microblog.py run.py  ./
COPY credentials.json ./

ENV FLASK_APP run.py
RUN chown -R microblog:microblog ./
USER microblog
EXPOSE 5000