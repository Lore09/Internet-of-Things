FROM python:3.9-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /app

COPY requirements.txt /app/requirements.txt

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV TZ="Europe/Rome"

COPY . /app

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]