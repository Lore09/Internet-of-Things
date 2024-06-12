FROM python:3.9-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /data_analysis

# set work directory
WORKDIR /data_analysis

COPY requirements.txt /data_analysis/requirements.txt

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV TZ="Europe/Rome"

COPY . /data_analysis

EXPOSE 5010

CMD ["fastapi", "dev", "app/main.py"]