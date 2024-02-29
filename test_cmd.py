#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

"""
Tests for the command line execution.
"""

import glob
import json
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

        path_to_assetmaster = os.path.join(current_dir, "assetmaster.py")

        lonmin = 50.0
        lonmax = 55.0
        latmin = 11.0
        latmax = 15.0
        schema = "SARA_v1.0"
        assettype = "res"
        querymode = "intersects"
        model = "ValpCVTBayesian"

        subprocess.run(
            [
                "python3",
                path_to_assetmaster,
                str(lonmin),
                str(lonmax),
                str(latmin),
                str(latmax),
                schema,
                assettype,
                querymode,
                model,
            ],
            check=True,
        )

        path_to_output_file = os.path.join(
            current_dir,
            "output",
            "query_output.geojson",
        )

        output = gpd.read_file(path_to_output_file)

        self.assertEqual(0, len(output))

    def test_in_peru(self):
        """
        Runs the test with a bounding box for peru.
        Must contain results.
        """

        current_dir = os.path.dirname(os.path.abspath(__file__))

        path_to_assetmaster = os.path.join(current_dir, "assetmaster.py")

        lonmin = -84.99
        lonmax = -67.63
        latmin = -18.81
        latmax = -3.33
        schema = "SARA_v1.0"
        assettype = "res"
        querymode = "intersects"
        exposure_models = [
            os.path.basename(d)
            for d in glob.glob(
                os.path.join(
                    current_dir,
                    "schemas",
                    "SARA_v1.0",
                    "Lima*",
                )
            )
        ]
        # We need to have several exposure models
        self.assertLess(0, len(exposure_models))
        for model in exposure_models:
            subprocess.run(
                [
                    "python3",
                    path_to_assetmaster,
                    str(lonmin),
                    str(lonmax),
                    str(latmin),
                    str(latmax),
                    schema,
                    assettype,
                    querymode,
                    model,
                ],
                check=True,
            )

            path_to_output_file = os.path.join(
                current_dir,
                "output",
                "query_output.geojson",
            )

            output = gpd.read_file(path_to_output_file)
            # And we get data for the queries for each single model
            self.assertLess(0, len(output))

    def test_in_chile(self):
        """
        Runs the test with a bounding box for chile.
        Must contain results.
        """

        current_dir = os.path.dirname(os.path.abspath(__file__))

        path_to_assetmaster = os.path.join(current_dir, "assetmaster.py")

        lonmin = -71.8
        lonmax = -71.4
        latmin = -33.2
        latmax = -33.0
        schema = "SARA_v1.0"
        assettype = "res"
        querymode = "intersects"

        models = [
            "ValpCVTBayesian",
            "ValpCommuna",
            "ValpRegularGrid",
            "ValpRegularOriginal",
            "ValpOBM23Comunas",
            "ValpOBM23Region",
        ]

        for model in models:

            subprocess.run(
                [
                    "python3",
                    path_to_assetmaster,
                    str(lonmin),
                    str(lonmax),
                    str(latmin),
                    str(latmax),
                    schema,
                    assettype,
                    querymode,
                    model,
                ],
                check=True,
            )

            path_to_output_file = os.path.join(
                current_dir,
                "output",
                "query_output.geojson",
            )

            output = gpd.read_file(path_to_output_file)

            self.assertLess(0, len(output))

    def test_in_ecuador_torres(self):
        """
        Runs the test with a bounding box for ecuador (torres).
        Must contain results.
        """

        current_dir = os.path.dirname(os.path.abspath(__file__))

        path_to_assetmaster = os.path.join(current_dir, "assetmaster.py")

        lonmin = -78.85
        lonmax = -78.43
        latmin = -1.05
        latmax = -0.62
        schema = "Torres_Corredor_et_al_2017"
        assettype = "res"
        querymode = "intersects"
        model = "LatacungaRuralAreas"

        subprocess.run(
            [
                "python3",
                path_to_assetmaster,
                str(lonmin),
                str(lonmax),
                str(latmin),
                str(latmax),
                schema,
                assettype,
                querymode,
                model,
            ],
            check=True,
        )

        path_to_output_file = os.path.join(
            current_dir,
            "output",
            "query_output.geojson",
        )

        output = gpd.read_file(path_to_output_file)

        self.assertLess(0, len(output))

        # test the data structure of the output
        with open(path_to_output_file, "r") as file:
            data = json.load(file)

        self.assertEqual("FeatureCollection", data.get("type"))

        features = data.get("features")

        self.assertLess(0, len(features))

        first = features[0]

        self.assertEqual("Feature", first.get("type"))
        self.assertIsNotNone(first.get("properties"))
        self.assertIsInstance(first.get("properties"), dict)
        self.assertIsNotNone(first.get("geometry"))
        self.assertIsInstance(first.get("geometry"), dict)

        properties = first.get("properties")

        self.assertIsNotNone(properties.get("gid"))
        self.assertIsNotNone(properties.get("name"))
        self.assertIsNotNone(properties.get("expo"))
        self.assertIsInstance(properties.get("expo"), dict)

        expo = properties.get("expo")

        self.assertIsNotNone(expo.get("id"))
        self.assertIsNotNone(expo.get("name"))
        self.assertIsNotNone(expo.get("Region"))
        self.assertIsNotNone(expo.get("Taxonomy"))
        self.assertIsNotNone(expo.get("Buildings"))
        self.assertIsNotNone(expo.get("Population"))
        self.assertIsNotNone(expo.get("Repl-cost-USD-bdg"))
        self.assertIsNotNone(expo.get("Damage"))

        geometry = first.get("geometry")

        self.assertIn(geometry.get("type"), ("MultiPolygon", "Polygon"))
        self.assertIsNotNone(geometry.get("coordinates"))

    def test_in_ecuador_mavrouli(self):
        """
        Runs the test with a bounding box for ecuador (mavrouli).
        Must contain results.
        """

        current_dir = os.path.dirname(os.path.abspath(__file__))

        path_to_assetmaster = os.path.join(current_dir, "assetmaster.py")

        lonmin = -78.85
        lonmax = -78.43
        latmin = -1.05
        latmax = -0.62
        schema = "Mavrouli_et_al_2014"
        assettype = "res"
        querymode = "intersects"
        model = "LatacungaRuralAreas"

        subprocess.run(
            [
                "python3",
                path_to_assetmaster,
                str(lonmin),
                str(lonmax),
                str(latmin),
                str(latmax),
                schema,
                assettype,
                querymode,
                model,
            ],
            check=True,
        )

        path_to_output_file = os.path.join(
            current_dir,
            "output",
            "query_output.geojson",
        )

        output = gpd.read_file(path_to_output_file)

        self.assertLess(0, len(output))


if __name__ == "__main__":
    unittest.main()
