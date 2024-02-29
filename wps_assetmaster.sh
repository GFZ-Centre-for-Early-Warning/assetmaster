#!/bin/bash

set -e

python3 assetmaster.py "$@"
python3 create_shapefile.py output/query_output.geojson
