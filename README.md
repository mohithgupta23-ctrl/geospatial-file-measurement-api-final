# Geospatial File Measurement API

A REST API for uploading and processing geospatial files such as KML files and ZIP archives containing Shapefiles.

The API extracts feature information, handles coordinate reference systems (CRS), and calculates measurements for supported geometries.

## Features

- Upload KML files
- Upload ZIP archives containing Shapefiles
- Extract geometry type
- Extract CRS information
- Extract feature properties/attributes
- Calculate polygon area
- Calculate LineString length
- Handle Point geometries without measurement
- Handle unsupported geometries gracefully
- Transform geographic CRS to a suitable projected CRS before calculating area or length
- Store uploaded file information in SQLite
- Store feature measurements in SQLite
- Retrieve file information through REST APIs
- Retrieve measurements through REST APIs
- Automated API tests using pytest

## Technology Stack

- Python
- FastAPI
- GeoPandas
- Shapely
- PyProj
- Fiona
- SQLAlchemy
- SQLite
- Pytest
- Uvicorn

## Project Structure

```text
Geospatial File Measurement API/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   └── services/
│       └── geospatial_service.py
│
├── tests/
│   └── test_api.py
│
├── uploads/
│   └── .gitkeep
│
├── .gitignore
├── README.md
└── requirements.txt