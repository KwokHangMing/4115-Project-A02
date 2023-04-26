FROM python:3.11.2-alpine
RUN adduser -D itp4115

WORKDIR /itp4115

ENV PYTHONUNBUFFERED 1


RUN apk add --no-cache --update gcc musl-dev libffi-dev openssl-dev
RUN python3 -m venv venv

COPY app app                                                                                                                                                     
COPY migrations migrations
COPY microblog.py run.py  ./
COPY credentials.json ./
COPY test_data.py ./
COPY requirements.txt requirements.txt
RUN pip install gunicorn
RUN pip install -r requirements.txt 

RUN chown -R itp4115:itp4115 ./
USER itp4115
EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["run.py"]