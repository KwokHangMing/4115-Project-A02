FROM python:3.11.2-alpine

WORKDIR /itp4115

COPY . .                                                                                                              
RUN pip3 install -r requirements.txt 


CMD ["python3", "run.py"]
