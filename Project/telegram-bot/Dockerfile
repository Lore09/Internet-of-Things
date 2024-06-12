FROM python:3.9-slim

# set work directory
WORKDIR /app

COPY requirements.txt /app/requirements.txt

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV TZ="Europe/Rome"

COPY . /app

CMD ["python3", "bot.py"]