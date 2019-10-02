# Assetmaster

[![Build Status](https://travis-ci.com/gfzriesgos/assetmaster.svg?branch=master)](https://travis-ci.com/gfzriesgos/assetmaster)

web service providing exposure models upon geographical query - RIESGOS project

This program reads an exposure model from a geopackage (.gpkg) file and provides a user with a portion of the model according to a bounding box provided (lonminm, lonmax, latmin, latmax), a query mode ("intersects" or "within").
A given exposure vulnerability schema can be queried (currently only the "SARA_v1.0" model for Chile is implemented)
A given set of assets can be specified (currently only "res" for residential buildings)

### example (command line)
python3.7 assetmaster.py -71.8 -71.4 -33.2 -33.0 SARA_v1.0 res intersects

### Dependencies
- argparse
- pandas 
- geopandas
- lxml
- shapely

### Process configuration 
The .json file providing the basic process configuration is in the *metadata* folder
