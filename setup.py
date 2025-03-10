"""Makes installable package."""

from setuptools import find_packages, setup
import pip

pip.main(["install"])  # call pip to install them

setup(
    name="QCmaps",
    version="0.0",
    author="QuantifiedCarbon",
    description="Package for map plotting",
    url="https://github.com/QuantifiedCarbon/QCmaps",
    packages=find_packages(),
    install_requires=["pandas", "geopandas", "matplotlib"],
    package_data={
        "QCmaps.data": ["el_zones_raew.geojson"],
    },
    include_package_data=True,  # This ensures that the files in MANIFEST.in are included
)
