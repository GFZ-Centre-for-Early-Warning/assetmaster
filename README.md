# Assetmaster

[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/gfzriesgos/assetmaster)](https://hub.docker.com/r/gfzriesgos/assetmaster)
[![Build Status](https://travis-ci.com/gfzriesgos/assetmaster.svg?branch=master)](https://travis-ci.com/gfzriesgos/assetmaster)

web service providing exposure models upon geographical query - RIESGOS project

This program reads an exposure model from a geopackage (.gpkg) file and provides a user with a portion of the model according to a bounding box provided (lonminm, lonmax, latmin, latmax), a query mode ("intersects" or "within").
A given exposure vulnerability schema can be queried (currently only the "SARA_v1.0" model for Chile is implemented)
A given set of assets can be specified (currently only "res" for residential buildings)

### Citation

Pittore, M., Gomez-Zapata, J. C., Brinckmann, N., Rüster, M. (2021): Assetmaster and Modelprop: web services to serve building exposure models and fragility functions for physical vulnerability to natural-hazards. V. 1.0. GFZ Data Services. https://doi.org/10.5880/riesgos.2021.005

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

### How to add data for other countries

If you just want to provide data for other countries you can add gpkg files
in the schemas/`<your schema here>`/ folders.

At least for the gpkg folder there is no naming convention inside of this folders
anymore.

The current version for SARA and Chile is the `schemas/SARA_v1.0/SARA_v1.0_data.gpkg`.
You can replace this with a new file.

For adding the peru exposure model for peru you can just insert the gpkg file into
the `schemas/SARA_v1/` folder. But please make sure that the data there matches the very
same structure of the existing gpkg data.

### Copyright & License
Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

### Project

Deus was developed in the scope of the RIESGOS project:
Multi-Risk Analysis and Information System Components for the Andes Region (https://www.riesgos.de/en)

