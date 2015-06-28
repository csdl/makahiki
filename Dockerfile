FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements-docker.txt /code/
RUN apt-get update && apt-get install -y libmemcached-dev
RUN pip install --allow-unverified PIL -r requirements-docker.txt
ADD . /code/
