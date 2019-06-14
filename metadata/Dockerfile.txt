FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install python3 git python3-scipy python3-numpy python3-pip libspatialindex-dev -y

RUN pip3 install geopandas Rtree lxml shapely

RUN mkdir /usr/share/git

RUN cd /usr/share/git && git clone https://github.com/GFZ-Centre-for-Early-Warning/assetmaster.git
