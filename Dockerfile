FROM debian:sid
FROM python:3.11

#RUN echo 'deb http://mirrors.psu.ac.th/debian/ sid main contrib non-free' > /etc/apt/sources.list

RUN apt update 
RUN apt install -y python3 python3-dev python3-pip python3-venv
RUN apt install -y nodejs npm

ENV LANG th_TH.UTF-8 
ENV LANGUAGE th_TH:en 

RUN python3 -m venv /venv
ENV PYTHON=/venv/bin/python3
RUN $PYTHON -m pip install wheel poetry gunicorn

WORKDIR /app

COPY mahjong/cmd /app/mahjong/cmd
COPY poetry.lock pyproject.toml /app/
RUN $PYTHON -m pip install --upgrade poetry
RUN $PYTHON -m poetry config virtualenvs.create false 
RUN . /venv/bin/activate && $PYTHON -m poetry install --no-interaction --only main 

COPY mahjong/web/static/package.json mahjong/web/static/package-lock.json mahjong/web/static/
RUN npm install --prefix mahjong/web/static

COPY . /app
ENV MAHJONG_SETTINGS=/app/mahjong-production.cfg