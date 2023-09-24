FROM python:3.11-slim

ARG APP

WORKDIR app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./$APP /app

COPY ./utils /app/utils

CMD python3 -u main.py
