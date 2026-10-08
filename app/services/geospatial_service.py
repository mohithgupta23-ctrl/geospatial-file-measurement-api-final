import json

import geopandas as gpd
import pandas as pd


def read_geospatial_file(file_path):
    """
    Read a supported geospatial file and return a GeoDataFrame.
    Supports KML and ZIP files containing a Shapefile.
    """

    if file_path.lower().endswith(".kml"):
        return gpd.read_file(file_path, driver="KML")

    if file_path.lower().endswith(".zip"):
        return gpd.read_file(f"zip://{file_path}")

    raise ValueError(
        "Unsupported file format. Only .kml and .zip files are supported."
    )


def get_measurements(file_path):
    """
    Extract feature information and calculate measurements.
    """

    gdf = read_geospatial_file(file_path)

    results = []

    original_crs = gdf.crs

    for index, feature in gdf.iterrows():

        geometry = feature.geometry

        if geometry is None:
            results.append({
                "feature_index": int(index),
                "geometry_type": "Unknown",
                "crs": str(original_crs),
                "measurement_type": None,
                "measurement_value": None,
                "properties": {}
            })
            continue

        geometry_type = geometry.geom_type

        properties = {}

        for column in gdf.columns:
            if column != "geometry":
                value = feature[column]

                if pd.isna(value):
                    properties[column] = None
                else:
                    try:
                        json.dumps(value)
                        properties[column] = value
                    except TypeError:
                        properties[column] = str(value)

        measurement_type = None
        measurement_value = None

        # Polygon → Area
        if geometry_type in ["Polygon", "MultiPolygon"]:

            measurement_type = "area"

            measurement_gdf = gpd.GeoDataFrame(
                [feature],
                geometry="geometry",
                crs=original_crs
            )

            if (
                measurement_gdf.crs
                and measurement_gdf.crs.is_geographic
            ):
                measurement_gdf = measurement_gdf.to_crs(
                    measurement_gdf.estimate_utm_crs()
                )

            measurement_value = float(
                measurement_gdf.geometry.area.iloc[0]
            )

        # LineString → Length
        elif geometry_type in ["LineString", "MultiLineString"]:

            measurement_type = "length"

            measurement_gdf = gpd.GeoDataFrame(
                [feature],
                geometry="geometry",
                crs=original_crs
            )

            if (
                measurement_gdf.crs
                and measurement_gdf.crs.is_geographic
            ):
                measurement_gdf = measurement_gdf.to_crs(
                    measurement_gdf.estimate_utm_crs()
                )

            measurement_value = float(
                measurement_gdf.geometry.length.iloc[0]
            )

        # Point → No measurement required
        elif geometry_type in ["Point", "MultiPoint"]:

            measurement_type = None
            measurement_value = None

        # Unsupported geometry → handle gracefully
        else:

            measurement_type = None
            measurement_value = None

        results.append({
            "feature_index": int(index),
            "geometry_type": geometry_type,
            "crs": str(original_crs),
            "measurement_type": measurement_type,
            "measurement_value": measurement_value,
            "properties": properties
        })

    return results