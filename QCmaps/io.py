"""Provides input/output functionalities."""

from pathlib import Path
import pandas as pd
import geopandas as gpd


def get_gdf():
    """
    Get geodataframe and formet it.

    Returns
    -------
    gpd.GeoDataFrame
        gdf, Geodataframe with Europe electricity bidding zones.
    """
    current_dir = Path(__file__).resolve().parent
    geo_data = gpd.read_file(current_dir / "data/el_zones_raew.geojson")
    gdf = geo_data[["id", "geometry"]].copy()
    gdf = gdf.set_index("id")
    return gdf


# dictionary with combination of zones
zones_agg = {
    "UK": ["GB", "NI"],
    "IESEM": ["IE", "NI"],
    "BT": ["EE", "LT", "LV"],
    "DELU": ["DE", "LU"],
    "DEATLU": ["DE", "AT", "LU"],
    "NO125": ["NO1", "NO2", "NO5"],
    "NO": ["NO1", "NO2", "NO3", "NO4", "NO5"],
    "SE": ["SE1", "SE2", "SE3", "SE4"],
    # "SE12": ["SE1", "SE2"], "SE34": ["SE3", "SE4"],
    "IT": ["IT1", "IT2", "IT3", "IT4", "IT5", "IT6"],
    "DK": ["DK1", "DK2"],
}


def process_gdf(df, gdf):
    """
    Process geo dataframe combining geometries with respect to zones in df.

    Add numerical values provided in df to gdf.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe with parameter values.
    gdf: gpd.GeoDataFrame
        Geodataframe with Europe electricity bidding zones.

    Returns
    -------
    gpd.GeoDataFrame
        gdf, Processes geodataframe with merged zones and parameter values.
    """
    remove_zones = []
    for zone in df.columns:
        if zone in zones_agg.keys():
            gdf_new = gdf[gdf.index.isin(zones_agg[zone])].dissolve()
            gdf_new.index = [zone]
            gdf = pd.concat([gdf, gdf_new])
            remove_zones = remove_zones + zones_agg[zone]
    gdf = gdf[~gdf.index.isin(remove_zones)]
    df = df.sort_index(axis=1)
    gdf = gdf.sort_index()
    for result in df.index:
        for zone in df.columns:
            gdf.loc[zone, result] = df.T.loc[zone, result]
    return gdf


def georeference(gdf, projection="equal_area"):
    """
    Geo reference gdf based on given projection.

    Default is equal area.

    Parameters
    ----------
    gdf: gpd.GeoDataFrame
        Processed Geodataframe.
    projection: str
        Type of projection.

    Returns
    -------
    gpd.GeoDataFrame
        gdf, Georeferenced Geodataframe.
    """
    if projection == "equal_area":
        crs = "EPSG:3035"
    if projection == "orthographic":
        zones = gdf.iloc[:, 1:].dropna(how="all").index
        centroid = (
            gdf.loc[zones].to_crs(epsg=3857).geometry.centroid.union_all().centroid
        )
        #        centroid = gdf[gdf.index == "PT"].to_crs(epsg=3857).geometry.centroid
        centroid = gpd.GeoSeries(centroid, crs="EPSG:3857").to_crs(epsg=4326)
        center_lon, center_lat = centroid.x[0], centroid.y[0]
        crs = f"+proj=ortho +lat_0={center_lat} +lon_0={center_lon} +datum=WGS84"
    gdf = gdf.to_crs(crs)
    return gdf
