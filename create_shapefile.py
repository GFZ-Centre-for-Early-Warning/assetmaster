#!/usr/bin/env python3

"""
Script to generate a shapefile out of the assetmaster output.

Background is that shapefiles can be send to a geoserver for
WMS outputs.
"""

import json
import pathlib
import sys

import geopandas
import pandas


class CustomColumnGenerator:
    """
    Generator for custom columns.

    Shapefile column names are very limited so we create c1, c2, ...
    and provide information to store the "real" names of those
    columns somewhere else.
    """

    def __init__(self, prefix):
        """Init the generator with a prefix."""
        self.prefix = prefix
        self.count = 1
        self.custom_column_names = {}
        self.custom_cols = {}

    def set_value_for_custom_column(self, long_name, id, value):
        """
        Set the value for a custom column.

        We use the id as mabye not all the rows have an entry
        for the specific custom column.
        """
        if long_name in self.custom_column_names.keys():
            col_name = self.custom_column_names[long_name]
        else:
            col_name = self._create_new_col()
            self.custom_column_names[long_name] = col_name
        self.custom_cols.setdefault(col_name, {})
        self.custom_cols[col_name][id] = value

    def _create_new_col(self):
        """Generate a new column name and increase the counter."""
        col_name = f"{self.prefix}{self.count}"
        self.count += 1
        return col_name

    def full_columns(self, id_array):
        """Return a dict with full lists for all the custom columns."""
        results = {}
        for col_name in self.custom_cols.keys():
            results[col_name] = []
            for id in id_array:
                results[col_name].append(self.custom_cols[col_name].get(id))
        return results

    def get_custom_column_mapping(self):
        """Return the mapping of the long names to the custom names."""
        return {v: k for k, v in self.custom_column_names.items()}


def main():
    """Create the shapefile and a helper file with the custom columns."""
    if len(sys.argv) < 2:
        print(
            "Usage python3 create_shapefile.py <jsonfile>",
            file=sys.stderr,
        )
        exit(1)
    filename_json_in = sys.argv[1]
    data_in = geopandas.read_file(filename_json_in)
    geometries = []
    ids = []
    n_buildings_per_cell = []
    custom_cols = CustomColumnGenerator(prefix="c")

    for _, row in data_in.iterrows():
        expo = row.expo
        gid = row.gid
        ids.append(gid)
        geometries.append(row.geometry)
        buildings_per_cell = 0

        for tax, n_buildings in zip(expo["Taxonomy"], expo["Buildings"]):
            custom_col_long_name = tax
            custom_cols.set_value_for_custom_column(
                long_name=custom_col_long_name, id=gid, value=n_buildings
            )
            buildings_per_cell += n_buildings
        n_buildings_per_cell.append(buildings_per_cell)
    df = pandas.DataFrame(
        {
            "id": ids,
            "buildings": n_buildings_per_cell,
            **custom_cols.full_columns(ids),
        }
    )
    gdf = geopandas.GeoDataFrame(df, geometry=geometries)
    gdf.crs = {"init": "EPSG:4326"}

    for ending in ["shp", "cpg", "dbf", "prj", "shx"]:
        filename = pathlib.Path(f"output/summary.{ending}")
        if filename.exists():
            filename.unlink()

    gdf.to_file("output/summary.shp")

    with open("output/meta_summary.json", "w") as outfile:
        json.dump(
            {
                "custom_columns": custom_cols.get_custom_column_mapping(),
            },
            outfile,
            separators=(",", ":"),
        )


if __name__ == "__main__":
    main()
