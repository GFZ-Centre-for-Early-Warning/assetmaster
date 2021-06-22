#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
# 
# https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

"""
This are the test cases for
making sure that the newly created
gpkg has the very same structure as the
old sara gpkg.
"""

import json
import os
import unittest

import geopandas as gpd
import pandas as pd

class TestStructureOfGpkg(unittest.TestCase):
    """
    Test case for making sure that the structure
    matches.
    """

    def test_same_structure_as_sara_model(self):
        """
        Test for making sure that the structure of the
        new valparaiso gpkg is the same as the
        one for the sara model.
        It tests both the columns of the very first element
        and the inner structure in the expo column.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        new_gpkg_path = os.path.join(current_dir, 'valparaiso_sara_data.gpkg')
        new_gpkg = gpd.read_file(new_gpkg_path)

        old_gpkg_path = os.path.join(
            current_dir,
            '..',
            'schemas',
            'SARA_v1.0',
            'SARA_v1.0_data.gpkg'
        )
        old_gpkg = gpd.read_file(old_gpkg_path)

        self.assertEqual(
            set(new_gpkg.columns),
            set(old_gpkg.columns)
        )

        old_expo1 = pd.DataFrame(json.loads(old_gpkg.iloc[0]['expo']))
        old_expo_columns = old_expo1.columns

        for _, row in new_gpkg.iterrows():
            new_expo = pd.DataFrame(json.loads(row['expo']))

            self.assertEqual(
                set(old_expo_columns),
                set(new_expo.columns)
            )


if __name__ == '__main__':
    unittest.main()


