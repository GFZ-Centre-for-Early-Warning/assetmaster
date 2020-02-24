#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 18:22:44 2019

@author: jcgomez
"""
import fiona

import warnings; warnings.filterwarnings("ignore")
import pandas as pd
import geopandas as gpd

import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import os
import folium

path = '/home/jcgomez/PowerFolders/riesgos (Massimiliano Pittore)/Exposure_Models/Exposure_Models_V1/Valparaiso/Model_0'
#infile = 'Cotopaxi_Exp_Lahar_Mavroulli_et_al_2014.csv'
infile = 'Tessalation_Valpo.csv'
#sara_data = pd.read_csv(data = gpd.read_file(fp)infile)
sara_data = pd.read_csv(infile, sep=',', encoding='latin-1')

#clean 'NOM_COMUNA' and use it as ID
#sara_data['TARGET_FID'] = sara_data.TARGET_FID.normalize('NFKD').encode('ascii', errors='ignore').decode('utf-8')
#save all names in an array
sara_names = sara_data['ID'].unique()

#group data based on 'NOM_COMUNA'
datagrp = sara_data.groupby('ID')
#a = datagrp.get_group(0)
#a

tax_lut = {"CR-LWAL-DNO-H-1-3",
        "CR-LWAL-DUC-H-1-3",
               "CR-PC-LWAL-H-1-3",
               "ER-ETR-H-1-2",
               "MCF-DNO-H-1-3",
               "MCF-DUC-H-1-3",
               "MR-DNO-H-1-3",
               "MR-DUC-H-1-3",
               "MUR-H-1-3",
               "MUR-ADO-H-1-2",
               "MUR-STDRE-H-1-2",
               "W-WLI-H-1-3", 
               "W-WS-H-1-2",
               "CR-LWAL-DNO-H-4-7",
               "CR-LWAL-DUC-H-4-7", 
               "CR-LWAL-DUC-H-8-19",
               "UNK"
               #ONE IS MISSING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
           }

#tax_props = {"W-WS-H1":{"Dwellings": 1,"Repl-cost-USD-bdg":35000,},
#            "W-WLI-H1":{}}

def updategroup(grp):
    group_tax = set(grp.taxonomy)
    droplist = []
    if 1:
        for i,item in grp.iterrows():
            if item.taxonomy in tax_lut:
                if item.taxonomy in group_tax:
                    #print (tax_lut[item.Taxonomy])
                    tg=grp[grp.taxonomy==item.taxonomy]
                    #print(tg.index)
                    grp.loc[tg.index,"Dwellings"] = -9999
                    grp.loc[tg.index,"Buildings"] = tg.SUM_Nij + item.SUM_Nij
                    grp.loc[tg.index,"Population"] = -9999
                    #tg.pop + item.pop
                    #put index in droplist
                    droplist.append(i)
    grp.drop(droplist,inplace=True)
    return(grp)


chile_map = 'Valparaiso_Vina_3000_FocusMap_60_40.shp'

data = gpd.read_file(chile_map)
chile_map_gpd = gpd.read_file(chile_map)
#chile_map_gpd['NOM_COMUNA'] = chile_map_gpd.TARGET_FID.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
hhh=len(chile_map_gpd)
#testg = datagrp.get_group("Aisen")
#updategroup(testg)

from shapely.geometry import MultiPolygon

outmodel = chile_map_gpd[[ 'ID', 'NOM_COMUNA', 'geometry']]


outmodel['expo'] = ""
#outmodel.head()
outmodel = outmodel.set_index('ID')

for gcname,gc in outmodel.iterrows():
    if (gcname in sara_names):
            testgrp = updategroup(datagrp.get_group(gcname))
            #add initial damage state - by default Null Damage (D0)
            testgrp['Damage'] = 'D0'
            outmodel.at[gcname,'expo'] = testgrp.to_json()
    #convert polygons into multipolygons to avoid errors in file output
    if (gc.geometry.geom_type == 'Polygon'):
        outmodel.at[gcname,'geometry'] = MultiPolygon([gc.geometry])

#outmodel['ID'] = outmodel['ID']
#outmodel = outmodel.reset_index()
#outmodel = outmodel[['name', ...]]
outmodel.columns = ['gid', 'geometry', 'expo']
#outmodel.columns = ['NOM_COMUNA','gid', 'geometry', 'expo']

outmodel = outmodel.reset_index()
outmodel.head()

#blacklist  = outmodel[outmodel.expo ==''].index
#outmodel1 = outmodel.drop(blacklist)

outpath = '/home/jcgomez/PowerFolders/riesgos (Massimiliano Pittore)/Exposure_Models/Exposure_Models_V1/Valparaiso/Model_0'
outfile =os.path.join(outpath,"Valparaiso_Vina_Model_3.gpkg")
outmodel.to_file(outfile, driver="GPKG")#,schema = ioschema)

#map_osa = folium.Map(location=[-32,-71],tiles='Stamen Terrain',zoom_start=10)
#map_osa.choropleth(geo_data=outmodel1,fill_opacity=0.3)




filename = "Valparaiso_Vina_Model_2.gpkg"
gdf = gpd.read_file(filename)

filename2="SARA_v1.0_data.gpkg"
gdf2 = gpd.read_file(filename2)