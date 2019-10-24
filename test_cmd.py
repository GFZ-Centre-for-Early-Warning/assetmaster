#!/usr/bin/env python3

"""
Tests for the command line execution.
"""

import os
import subprocess
import unittest

import geopandas as gpd


class TestCmdExecution(unittest.TestCase):
    """
    Test case for the command line execution.
    """

    def test_in_germany(self):
        """
        Runs the test with a bounding box for chile.
        Must not contain results.
        """

        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        path_to_assetmaster = os.path.join(
            current_dir,
            'assetmaster.py'
        )

        lonmin = 50.0
        lonmax = 55.0
        latmin = 11.0
        latmax = 15.0
        schema = 'SARA_v1.0'
        assettype = 'res'
        querymode = 'intersects'

        subprocess.run(
            [
                'python3',
                path_to_assetmaster,
                str(lonmin),
                str(lonmax),
                str(latmin),
                str(latmax),
                schema,
                assettype,
                querymode
            ],
            check=True,
        )

        path_to_output_file = os.path.join(
            current_dir,
            'output',
            'query_output.geojson',
        )

        output = gpd.read_file(path_to_output_file)

        self.assertEqual(0, len(output))


    def test_in_chile(self):
        """
        Runs the test with a bounding box for chile.
        Must contain results.
        """

        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        path_to_assetmaster = os.path.join(
            current_dir,
            'assetmaster.py'
        )

        lonmin = -71.8
        lonmax = -71.4
        latmin = -33.2
        latmax = -33.0
        schema = 'SARA_v1.0'
        assettype = 'res'
        querymode = 'intersects'

        subprocess.run(
            [
                'python3',
                path_to_assetmaster,
                str(lonmin),
                str(lonmax),
                str(latmin),
                str(latmax),
                schema,
                assettype,
                querymode
            ],
            check=True,
        )

        path_to_output_file = os.path.join(
            current_dir,
            'output',
            'query_output.geojson',
        )

        output = gpd.read_file(path_to_output_file)

        self.assertLess(0, len(output))

if __name__ == '__main__':
    unittest.main()
