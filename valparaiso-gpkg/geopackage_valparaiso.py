#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
# 
# https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

"""
This code should create a valparaiso gpkg file,
similar the way Camilo did in the OldGeopackage_Valparaiso.py
file and as Max did in the assetmaster_modelcreator.ipynb
"""

import os
import pdb

import pandas as pd
import geopandas as gpd

def get_geometry_and_assume_all_are_equal(geom_series):
    all_equal = True

    first_geom = None
    for geom in geom_series:
        if first_geom is None:
            first_geom = geom
        if first_geom != geom:
            all_equal = False
            break

    assert(all_equal)

    return first_geom

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # we have two input files
    # one is a csv with some of the building class related
    # data
    #
    # the other one is for the spatial data (and is a shp file)
    #
    # both are connected via the ID and taxonomy (one time
    # uppercase on time lower case) parameter

    # so lets read the files
    # first the csv file
    csv_path = os.path.join(current_dir, 'Tessalation_Valpo.csv')
    csv_data = pd.read_csv(csv_path)
    # second the map
    map_path = os.path.join(current_dir, 'TessellationsComuna.shp')
    map_data = gpd.read_file(map_path)

    # group by ID
    # as we want one geocell for each ID

    csv_data_by_id = csv_data.groupby('ID')
    map_data_by_id = map_data.groupby('ID')

    # just make sure that we care about the very same ids
    assert(csv_data_by_id.groups.keys() == map_data_by_id.groups.keys())

    outer_series_list = []

    for gid in csv_data_by_id.groups.keys():
        csv_for_gid = csv_data_by_id.get_group(gid)
        map_for_gid = map_data_by_id.get_group(gid)
        possible_names = map_for_gid['name'].unique()

        assert(len(possible_names) == 1)

        # we already have the gid
        # so get the other values here
        # that we need in the toplevel to have the very
        # same structure as in the old sara model
        # for chile
        name = possible_names[0]
        geometry = get_geometry_and_assume_all_are_equal(map_for_gid['geometry'])

        csv_by_tax = csv_for_gid.groupby('taxonomy')
        map_by_tax = map_for_gid.groupby('Taxonomy')

        assert(csv_by_tax.groups.keys() == map_by_tax.groups.keys())

        inner_series_list = []

        for taxonomy in csv_by_tax.groups.keys():
            csv_for_tax = csv_by_tax.get_group(taxonomy)
            map_for_tax = map_by_tax.get_group(taxonomy)

            assert(len(csv_for_tax) == 1)
            assert(len(map_for_tax) == 1)

            inner_series = pd.Series({
                'id': 'AREA # ' + gid,
                'Region': name,
                'Taxonomy': taxonomy,
                'Dwellings': map_for_tax.iloc[0]['Dwellings'],
                'Buildings': map_for_tax.iloc[0]['Buildings'],
                'Repl-cost-USD-bdg': map_for_tax.iloc[0]['Repl_cost_'],
                'Population': map_for_tax.iloc[0]['Population'],
                'name': name,
                'Damage': 'D0',
            })

            inner_series_list.append(inner_series)

        expo = pd.DataFrame(inner_series_list)

        outer_series = pd.Series({
            'name': name,
            'gid': gid,
            'expo': expo.to_json(),
            'geometry': geometry,
        })

        outer_series_list.append(outer_series)

    outmodel = pd.DataFrame(outer_series_list)
    outmodel = gpd.GeoDataFrame(outmodel, geometry=outmodel['geometry'])

    out_path = os.path.join(current_dir, 'valparaiso_sara_data.gpkg')

    outmodel.to_file(out_path, driver='GPKG')


if __name__ == '__main__':
    main()
