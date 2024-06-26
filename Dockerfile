FROM python:3.8
WORKDIR /app

ENV TZ="Europe/Rome"
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python3", "./app.py"]