#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
# 
# https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

"""
Test cases for testing the model provider
module.
"""

import unittest

import pandas as pd
import geopandas as gpd

from shapely.geometry import box

import modelprovider

class TestMultiModelProvider(unittest.TestCase):
    """
    Test case for the MultiModelProvider class.
    """

    def setUp(self):
        """
        Sets up the multi model setting.
        """
        # ~~ germany
        geom1 = self._geom_from_bounding_box(lonmin=50, lonmax=55, latmin=10, latmax=15)
        # ~~ chile
        geom2 = self._geom_from_bounding_box(lonmin=-80, lonmax=-65, latmin=-70, latmax=-30)

        df1 = pd.DataFrame({
            'name': ['germany'],
            'geometry': [geom1]
        })

        df2 = pd.DataFrame({
            'name': ['chile'],
            'geometry': [geom2]
        })
        crs = {'init': 3226}

        gdf1 = gpd.GeoDataFrame(df1, crs=crs, geometry=df1['geometry'])
        gdf2 = gpd.GeoDataFrame(df2, crs=crs, geometry=df2['geometry'])

        model_provider1 = modelprovider.ModelProvider(gdf1)
        model_provider2 = modelprovider.ModelProvider(gdf2)

        self.model_provider = modelprovider.MultiModelProvider(models=[model_provider1, model_provider2])

        # search for the whole world
        self.roi_world = gpd.GeoDataFrame(
            index=[0],
            crs=crs,
            geometry=[self._geom_from_bounding_box(lonmin=-180, lonmax=180, latmin=-90, latmax=90)]
        )
        # search only for NE hemisphere
        self.roi_ne = gpd.GeoDataFrame(
            index=[0], 
            crs=crs,
            geometry=[self._geom_from_bounding_box(lonmin=0, lonmax=180, latmin=0, latmax=90)]
        )
        self.roi_smaller_g = gpd.GeoDataFrame(
            index=[0], 
            crs=crs, 
            geometry=[self._geom_from_bounding_box(lonmin=51, lonmax=54, latmin=11, latmax=14)]
        )

    def _geom_from_bounding_box(self, lonmin, lonmax, latmin, latmax):
        self.assertLess(lonmin, lonmax)
        self.assertLess(latmin, latmax)
        return box(minx=lonmin, maxx=lonmax, miny=latmin, maxy=latmax)

    def test_within(self):
        """
        Tests the within method.
        It should only give back the elements
        from the model if the elements are completely in the roi.
        """

        models_within_world = self.model_provider.within(self.roi_world)
        models_within_ne = self.model_provider.within(self.roi_ne)
        models_within_smaller_g = self.model_provider.within(self.roi_smaller_g)

        self.assertEqual(len(models_within_world), 2)
        self.assertEqual(len(models_within_ne), 1)
        self.assertEqual(len(models_within_smaller_g), 0)

        self.assertEqual(type(models_within_world), gpd.GeoDataFrame)

    def test_intersects(self):
        """
        Tests the intersection method.
        It should only give back the elements from the model
        that intersects with the roi.
        """
        models_intersection_world = self.model_provider.intersects(self.roi_world)
        models_intersection_ne = self.model_provider.intersects(self.roi_ne)
        models_intersection_smaller_g = self.model_provider.intersects(self.roi_smaller_g)

        self.assertEqual(len(models_intersection_world), 2)
        self.assertEqual(len(models_intersection_ne), 1)
        self.assertEqual(len(models_intersection_smaller_g), 1)

        self.assertEqual(type(models_intersection_world), gpd.GeoDataFrame)


class TestModelProvider(unittest.TestCase):
    """
    Test case for the ModelProvider class.
    """

    def setUp(self):
        """
        Sets one geodataframe and the model provider
        instance.
        """

        # ~~ germany
        geom1 = self._geom_from_bounding_box(lonmin=50, lonmax=55, latmin=10, latmax=15)
        # ~~ chile
        geom2 = self._geom_from_bounding_box(lonmin=-80, lonmax=-65, latmin=-70, latmax=-30)

        df = pd.DataFrame({
            'name': ['germany', 'chile'],
            'geometry': [geom1, geom2]
        })

        crs = {'init': 3226}

        gdf = gpd.GeoDataFrame(df, crs=crs, geometry=df['geometry'])

        self.model_provider = modelprovider.ModelProvider(gdf)

        # search for the whole world
        self.roi_world = gpd.GeoDataFrame(
            index=[0],
            crs=crs,
            geometry=[self._geom_from_bounding_box(lonmin=-180, lonmax=180, latmin=-90, latmax=90)]
        )
        # search only for NE hemisphere
        self.roi_ne = gpd.GeoDataFrame(
            index=[0], 
            crs=crs,
            geometry=[self._geom_from_bounding_box(lonmin=0, lonmax=180, latmin=0, latmax=90)]
        )
        self.roi_smaller_g = gpd.GeoDataFrame(
            index=[0], 
            crs=crs, 
            geometry=[self._geom_from_bounding_box(lonmin=51, lonmax=54, latmin=11, latmax=14)]
        )

    def _geom_from_bounding_box(self, lonmin, lonmax, latmin, latmax):
        self.assertLess(lonmin, lonmax)
        self.assertLess(latmin, latmax)
        return box(minx=lonmin, maxx=lonmax, miny=latmin, maxy=latmax)

    def test_within(self):
        """
        Tests the within method.
        It should only give back the elements
        from the model if the elements are completely in the roi.
        """

        models_within_world = self.model_provider.within(self.roi_world)
        models_within_ne = self.model_provider.within(self.roi_ne)
        models_within_smaller_g = self.model_provider.within(self.roi_smaller_g)

        self.assertEqual(len(models_within_world), 2)
        self.assertEqual(len(models_within_ne), 1)
        self.assertEqual(len(models_within_smaller_g), 0)

        self.assertEqual(type(models_within_world), gpd.GeoDataFrame)

    def test_intersects(self):
        """
        Tests the intersection method.
        It should only give back the elements from the model
        that intersects with the roi.
        """
        models_intersection_world = self.model_provider.intersects(self.roi_world)
        models_intersection_ne = self.model_provider.intersects(self.roi_ne)
        models_intersection_smaller_g = self.model_provider.intersects(self.roi_smaller_g)

        self.assertEqual(len(models_intersection_world), 2)
        self.assertEqual(len(models_intersection_ne), 1)
        self.assertEqual(len(models_intersection_smaller_g), 1)

        self.assertEqual(type(models_intersection_world), gpd.GeoDataFrame)


if __name__ == '__main__':
    unittest.main()
