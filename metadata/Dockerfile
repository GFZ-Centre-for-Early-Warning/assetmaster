FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install python3 git python3-pip libspatialindex-dev -y

WORKDIR /usr/share/git/assetmaster

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .
