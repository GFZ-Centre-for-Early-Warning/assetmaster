#!/usr/bin/env python3

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


