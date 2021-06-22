#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
# 
# https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

"""
This is the module for the model provider
classes for accessing for example
geopackage files.
"""

import geopandas as gpd
import pandas as pd

class ModelProvider():
    """
    Class to return the parts of the
    model that are within or intersects
    an given region of interest (roi).
    """
    def __init__(self, gdf):
        self.gdf = gdf

    def within(self, roi):
        geom = roi.geometry.iloc[0]
        are_within = self.gdf.within(geom)
        return self.gdf[are_within]

    def intersects(self, roi):
        geom = roi.geometry.iloc[0]
        are_intersects = self.gdf.intersects(geom)
        return self.gdf[are_intersects]

    @classmethod
    def from_file(cls, filename):
        gdf = gpd.read_file(filename, encoding='utf-8')
        return cls(gdf)

class MultiModelProvider():
    def __init__(self, models):
        self.models = models

    def within(self, roi):
        subresults = [submodel.within(roi) for submodel in self.models]
        return pd.concat(subresults, ignore_index=True)

    def intersects(self, roi):
        subresults = [submodel.intersects(roi) for submodel in self.models]
        return pd.concat(subresults, ignore_index=True)

