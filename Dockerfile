FROM ubuntu:18.04

MAINTAINER Eryk Kropiwnicki <eryk.kropiwnicki@icahn.mssm.edu>

# Python installs
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools

RUN python3 -m pip install --upgrade pip

# pip installs
RUN pip3 install --upgrade pip
RUN pip3 install flask
RUN pip3 install flask-cors
RUN pip3 install Flask-Session
RUN pip3 install h5py
RUN pip3 install pandas
RUN pip3 install numpy
RUN pip3 install requests
RUN pip3 install python-dateutil --upgrade

RUN mkdir -p /app/similarity
COPY . /app

EXPOSE 5000

WORKDIR /app

RUN chmod -R 777 /app
ENTRYPOINT ./entrypoint.sh
