#!/usr/bin/env/python

# coding: utf-8

'''
utilities to write an exposure geo-data model into 
openquake-compliant nrml (xml) format.
'''


import argparse
import sys
import pandas as pd
import os
import csv
import json
from lxml import etree

#used by the nrml 
NAMESPACE = 'http://openquake.org/xmlns/nrml/0.5'
GML_NAMESPACE = 'http://www.opengis.net/gml'
SERIALIZE_NS_MAP = {None: NAMESPACE, 'gml': GML_NAMESPACE}


'''
Read a dictionary from a csv file
'''
def load_expo_dicts(infile):
    with open(infile, 'rt') as f:
        dicts  = []
        reader = csv.DictReader(f)
        for row in reader:
            dicts.append(row)
        return pd.DataFrame(dicts)
    
'''
Write to disk a dictionary as a csv file
'''
def write_expo_dicts(dicts,outfile):
    with open(outfile, 'wb') as f: 
        w = csv.DictWriter(f, dicts[0].keys())
        w.writeheader()
        for d in dicts:
            w.writerow(d)
            
'''
Return the properties of a specific asset type, described by the taxonomy 'type'
'''
def get_btype_dicts(btype,dictionary):
    return(dictionary.loc[dictionary['btype']==btype].iloc[0])

'''
Read metadata from a json file
'''
def read_metadata(infile):
    with open(infile, 'r') as file:
        s = file.read()
        m = json.loads(s)
        return(m)


'''
Export an exposure model, asset-based, in nrml05 (openquake) format.

inputs: 

data: geopandas dataframe with as many rows as the number of geocells. Each geocell 
is described by its boundary polygon (column "geometry"), its unique id (column "index") and its 
name (column "gc_id"). The taxonomies of the assets are additional columns, and the corresponding 
row elements gives the expexted number of assets of this type in the geocell.  

metadata: dictionary of metadata necessary to describe the exposure model (see OpenQuake doc).
an example follows

metadata['id']='test_v0.1'
metadata['category'] = 'buildings'
metadata['taxonomy_source'] = 'RIESGOS'
metadata['description'] = 'test valparaiso'
metadata['structural_cost_aggregation_type'] = 'per_asset'
metadata['structural_cost_currency'] = 'USD'
metadata['nonstructural_cost_aggregation_type'] = False
metadata['contents_cost_aggregation_type'] = False
metadata['insurance_deductible_is_absolute'] = False
metadata['insurance_limit_is_absolute'] = False
metadata['taxonomies'] = ["tax1","tax2","tax3"]


dicts: dictionary with the main properties of the assets. The taxonomies (btype) must match

taxonomies: an explicit list of the taxonomies in the "data" dataframe.

output_xml: name of the output file. if the filename is empty, no file will be exported

'''
def write_nrml05_expo(data,metadata,dicts,taxonomies,output_xml):
    
    root = etree.Element('nrml', nsmap=SERIALIZE_NS_MAP)
    node_em = etree.SubElement(root, "exposureModel")
    node_em.set("id", metadata['id'])
    node_em.set("category", metadata['category'])
    node_em.set("taxonomySource", metadata['taxonomy_source'])

    node_desc = etree.SubElement(node_em, "description")
    node_desc.text = metadata['description']
    node_conv = etree.SubElement(node_em, "conversions")
    node_cost_types = etree.SubElement(node_conv, "costTypes")

    node_cost_type_s = etree.SubElement(node_cost_types, "costType")
    node_cost_type_s.set("name", "structural")
    node_cost_type_s.set("type", metadata['structural_cost_aggregation_type'])
    node_cost_type_s.set("unit", metadata['structural_cost_currency'])

    if metadata['nonstructural_cost_aggregation_type']:
        node_cost_type_ns = etree.SubElement(node_cost_types, "costType")
        node_cost_type_ns.set("name", "nonstructural")
        node_cost_type_ns.set("type", metadata['nonstructural_cost_aggregation_type'])
        node_cost_type_ns.set("unit", metadata['nonstructural_cost_currency'])
    if metadata['contents_cost_aggregation_type']:
        node_cost_type_c = etree.SubElement(node_cost_types, "costType")
        node_cost_type_c.set("name", "contents")
        node_cost_type_c.set("type", metadata['contents_cost_aggregation_type'])
        node_cost_type_c.set("unit", metadata['contents_cost_currency'])

    if metadata['insurance_deductible_is_absolute']:
        node_deductible = etree.SubElement(node_conv, "deductible")
        node_deductible.set("isAbsolute", metadata['insurance_deductible_is_absolute'].lower())
    if metadata['insurance_limit_is_absolute']:
        node_limit= etree.SubElement(node_conv, "insuranceLimit")
        node_limit.set("isAbsolute", metadata['insurance_limit_is_absolute'].lower())

    node_assets = etree.SubElement(node_em, "assets")

    #iterate on the geocells
    for gid, item in data.iterrows():
        #check if is empty
        if item.expo == '':
            continue
        geocell = pd.DataFrame(json.loads(item.expo))
        geocell_geometry= item.geometry
        
        #this can be used to vary the cost locally. Currently not used
        cost_coeff = 1.0
        #iterate on the taxonomies in the geocell
        for ir,bdg_item in geocell.iterrows():

            #number of buildings of this building type
            num_buildings = bdg_item.Buildings

            if (num_buildings > 0):
                btype = bdg_item.Taxonomy

                #get properties of this building type
                bdg_prop = get_btype_dicts(btype,dicts)
                
                asset_id = str(bdg_item.id)

                node_asset = etree.SubElement(node_assets, "asset")
                node_asset.set("id", asset_id)
                node_asset.set("number", str(int(num_buildings+0.5)))
                node_asset.set("taxonomy", str(btype))

                #location is the one of the corresponding geocell
                #Note: since geometry is multipolygon, actual location 
                #may be outside of geocell boundaries
                node_location = etree.SubElement(node_asset, "location")
                node_location.set("lon", str(geocell_geometry.centroid.x))
                node_location.set("lat", str(geocell_geometry.centroid.y))

                #structural cost
                node_costs = etree.SubElement(node_asset, "costs")
                node_cost_s = etree.SubElement(node_costs, "cost")
                node_cost_s.set("type", 'structural')

                str_val = float(bdg_prop['avg_struct_cost'])*cost_coeff
                node_cost_s.set("value", str(str_val))

                # occupancy in terms of inhabitants 
                node_occupancies = etree.SubElement(node_asset, "occupancies")
                node_occ_day = etree.SubElement(node_occupancies, "occupancy")
                node_occ_day.set("period", 'day')
                node_occ_day.set("occupants", str(bdg_prop['nocc_day']))

                node_occ_night = etree.SubElement(node_occupancies, "occupancy")
                node_occ_night.set("period", 'night')
                node_occ_night.set("occupants", str(bdg_prop['nocc_night']))

            #else:
                #print('skipping')

    output_string = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    
    # ok write information on the exposure file
    if (output_xml != ''):
        with open(output_xml, "wb") as f:
            f.write(output_string)
        
    return(output_string)
