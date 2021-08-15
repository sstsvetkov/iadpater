FROM python:3.8-alpine
WORKDIR /usr/src/iadapter

RUN apk update

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src .
