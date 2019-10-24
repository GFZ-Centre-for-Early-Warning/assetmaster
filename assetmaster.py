#!/usr/bin/env python3

'''
Assetmaster
-----------------
Command line program to query exposure data from a database/file.
'''

import argparse
import os
import geopandas as gp
from geopandas.io.file import infer_schema
from shapely.geometry import Polygon
#import matplotlib
#import matplotlib.pyplot as plt
import expo_nrml as nrml

class Main():
    '''
    Main class to execute
    '''
    def __init__(self, args):
        self.folder = os.path.dirname(__file__)

        # command line arguments
        self.lonmin = args.lonmin
        self.lonmax = args.lonmax
        self.latmin = args.latmin
        self.latmax = args.latmax
        self.schema = args.schema
        self.assettype = args.assettype
        self.querymode = args.querymode
        
        #i/o settings
        self.path_expo_dict = self.folder
        self.path_metadatefile = self.folder
        self.path_infile = self.folder
        self.in_file = self.folder
        self.dict_file = self.folder
        self.metadata_file = self.folder
        self.path_outfile = os.path.join(self.folder,"output")
        self.out_file_xml = "query_output.xml"
        self.out_file_geojson = 'query_output.geojson'
        
        self.roi = None
        self.metadata = None
        self.dicts = None 
        self.taxonomies = None

        #list of supported schemas. 
        #TODO: automatically parse them from a given folder
        self.supported_schemas = ['SARA_v1.0']
        
        #list of supported query modes
        self.supported_querymodes = ['intersects','within']

        # in case there is some deaggregation necessary
        # precision
        self.precision_lon = 0
        self.precision_lat = 0

        # result
        self.query_result = None

    def _compute_roi(self):
        lat_point_list = [self.latmin,self.latmax ,self.latmax, self.latmin,self.latmin]
        lon_point_list = [self.lonmin, self.lonmin,self.lonmax,self.lonmax,self.lonmin]
        roi_geom = Polygon(zip(lon_point_list, lat_point_list))
        crs = {'init': 'epsg:4326'}
        self.roi = gp.GeoDataFrame(index=[0], crs=crs, geometry=[roi_geom])       

    def _check_schema(self):
        return(set([self.schema]) <= set(self.supported_schemas))

    def _check_querymode(self):
        return(set([self.querymode]) <= set(self.supported_querymodes))

    def _check_longitude(self):
        '''If there is a longitude > 180 than it should be converted'''
        if self.lonmin > 180:
            self.lonmin = Main._convert_360(self.lonmin)
        if self.lonmax > 180:
            self.lonmax = Main._convert_360(self.lonmax)
            
    @staticmethod
    def _convert_360(lon):
        '''
        convert a longitude specified with 180+
        '''
        return lon-360
    
        
    def read_model(self,input_file):
        '''
        read exposure model from a (geopackage) file, 
        geometry: multipolygon
        columns: 
        fid= (int) id of the geocell
        name= (str) name of the geocell 
        expo= (str) exposure model for the geocell. 
                    Each expo element is a json dictionary containing:
                    index= unique index of the geocell
                    id= id of the geocell
                    Region = name of the geocell
                    Taxonomy = taxonomic type
                    Dwellings = no. of dwellings per taxonomic type in the geocell (optional)
                    Buildings = no. of buildings per taxonomic type in the geocell 
                    Repl_cost_USD/bdg = replacement cost per building per taxonomic type in USD (optional)
                    Population = total population per taxonomic type in the geocell (optional)
                    
        returns the model as geopandas dataframe
        '''
        #init model
        #input_file = 'schemas/SARA_v1.0/SARA_v1.0_data.gpkg'
        res = gp.read_file(input_file,encoding = 'utf-8')
        
        #taxonomies = res.keys()[res.dtypes=='float64']
        #cols = ['GID_3','NAME_3','geometry',*taxonomies.values]
        #out = res[cols].reset_index()
        #out.columns = ['index','gc_id','name','geometry',*taxonomies.values]
        return (res)
    
    def queryModelfromRoi(self,mod,roi,mode='within'):
        '''
        extract a part of the model by doing a spatial query on the geopandas df
        return a sub-portion of a model based on a ROI and a query mode: 
        'within': returns the geometries that are completely inside the ROI
        'intersects': returns the geometries that are intersecting the ROI
        '''
        r = roi.geometry.iloc[0]
        if (mode=='within'):
            res=mod[mod.within(r)]
        elif(mode=='intersects'):
            res=mod[mod.intersects(r)]
        else:
            raise Exception ('queryModelfromRoi: unknown mode')
        return(res)
    
    def _exportGeoJson(self, dataframe, filename):
        '''
        Export geopandas dataframe as GeoJson file
        '''
        # file has to be first deleted
        # because driver does not support overwrite ! 
        try: 
            os.remove(filename)
        except OSError:
            #print("OS Error removing geojson file")
            pass
        # this is the fallback schema for empty dataframes
        # since geojson just contains no elements
        # its fine to not provide any columns
        fallback_schema = {
            'geometry': 'MultiPolygon',
            'properties': {}
        }
        if dataframe.empty:
            schema = fallback_schema
        else:
            schema = infer_schema(dataframe)
        dataframe.to_file(filename, driver='GeoJSON', schema=schema)
        return (0)

    def _exportNrml05(self, dataframe, filename, metadata, dicts,taxonomies):
        '''
        Export geopandas dataframe as nrml file
        '''
        # remove file if exists
        try: 
            os.remove(filename)
        except OSError:
            #print("OS Error removing nrml file")
            pass
        xml_string = nrml.write_nrml05_expo(dataframe,metadata,dicts,taxonomies,filename)
        return (0)

    def _write_outputs(self):
        '''
        Export query result as nrml and geojson files
        '''
        output_geojson = os.path.join(self.path_outfile,self.out_file_geojson)
        self._exportGeoJson(self.query_result,output_geojson)
        output_xml = os.path.join(self.path_outfile,self.out_file_xml)
        self._exportNrml05(self.query_result, output_xml, self.metadata, 
                           self.dicts,self.taxonomies)
    
    def run(self):
        '''
        Method to:
        - connect with the database
        - query the database
        - do some deaggregation if necessary
        - write the output
        '''

        self._check_longitude()
        self._compute_roi()
        
        if (self._check_schema()):
            foldername = os.path.join(self.folder,"schemas/{}".format(self.schema))
            self.path_expo_dict = foldername
            self.path_metadatefile = foldername
            self.path_infile = foldername
            self.in_file = "{}_data.gpkg".format(self.schema)
            self.dict_file = "{}_prop.csv".format(self.schema)
            self.metadata_file = "{}_meta.json".format(self.schema)
        else:
            raise Exception ("schema {} not supported".format(self.schema))

        #read the exposure model metadata (with the list of taxonomies)
        self.metadata = nrml.read_metadata(os.path.join(self.path_metadatefile,self.metadata_file))
        self.taxonomies = self.metadata['taxonomies']
        #print(self.taxonomies)
        
        #get a dataframe with the basic properties of the buildings
        self.dicts = nrml.load_expo_dicts(os.path.join(self.path_expo_dict,self.dict_file))

        #read taxonomies from the dict file
        btypes = self.dicts.btype

        #check that the asset taxonomies match
        if not (set(self.taxonomies) <= set(btypes)):
            raise Exception ("taxonomies do not match")
            return (1)

        #read model from file 
        in_file = os.path.join(self.path_infile,self.in_file)
        self.model = self.read_model(in_file)

        #spatial query
        if (self._check_querymode()):
            self.query_result = self.queryModelfromRoi(self.model,self.roi,self.querymode)
        else:
            raise Exception ("Query mode {} not supported".format(self.querymode))
            return (1)
        
        self._write_outputs()
        return (0)


    @classmethod
    def create_with_arg_parser(cls):
        '''
        Creates an arg parser and uses that to create the Main class
        '''
        arg_parser = argparse.ArgumentParser(
            description='''Program to query an exposure model from a database/file'''
        )
        arg_parser.add_argument(
            'lonmin',
            help='Region Of Interest: Minimal longitude',
            type=float,
            default=-71.8)
        arg_parser.add_argument(
            'lonmax',
            help='Region Of Interest: Maximal longitude',
            type=float,
            default=-71.4)
        arg_parser.add_argument(
            'latmin',
            help='Region Of Interest: Minimal latitude',
            type=float,
            default=-33.2)
        arg_parser.add_argument(
            'latmax',
            help='Region Of Interest: Maximal latitude',
            type=float,
            default=-33.0)
        arg_parser.add_argument(
            'schema',
            help='Exposure/Vulnerability Schema',
            type=str,
            default="SARA_v1.0")
        arg_parser.add_argument(
            'assettype',
            help='Type of exposed assets',
            type=str,
            default='res')
        arg_parser.add_argument(
            'querymode',
            help='''Query Mode ('contains' / 'intersects')''',
            type=str,
            default='intersects')
        args = arg_parser.parse_args()
        #print(args)

        return cls(args)

if __name__ == '__main__':
    Main.create_with_arg_parser().run()
