# FROM python:3.11.2-alpine
# RUN adduser -D itp4115

# WORKDIR /itp4115

# ENV PYTHONUNBUFFERED 1


# COPY requirements.txt requirements.txt
# RUN apk add --no-cache --update gcc musl-dev libffi-dev openssl-dev
# RUN python3 -m venv venv
# RUN pip install -r requirements.txt 
# RUN pip install --upgrade pip
# RUN pip install gunicorn

# COPY app app                                                                                                                                                     
# COPY migrations migrations
# COPY microblog.py run.py  ./
# COPY credentials.json ./
# COPY test_data.py ./

# RUN chown -R itp4115:itp4115 ./
# USER microblog
# EXPOSE 5000
# ENTRYPOINT ["python3"]
# CMD ["run.py"]