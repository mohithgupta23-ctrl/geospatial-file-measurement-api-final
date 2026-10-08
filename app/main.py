import json
import shutil
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.models import Measurement, UploadedFile
from app.services.geospatial_service import get_measurements


app = FastAPI(
    title="Geospatial File Measurement API",
    description="API for processing geospatial files and calculating feature measurements.",
    version="1.0.0"
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# Create database tables when the application starts
init_db()


@app.get("/")
def home():
    return {
        "message": "Geospatial File Measurement API is running"
    }


@app.post("/api/files/")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required"
        )

    filename = file.filename.lower()

    if not (
        filename.endswith(".kml")
        or filename.endswith(".zip")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only .kml and .zip files are supported"
        )

    extension = Path(filename).suffix

    saved_path = UPLOAD_DIR / f"{file.filename}"

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    uploaded_file = UploadedFile(
        filename=file.filename,
        file_type=extension.replace(".", ""),
        status="processing"
    )

    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    try:
        measurements = get_measurements(str(saved_path))

        for result in measurements:

            measurement = Measurement(
                file_id=uploaded_file.id,
                feature_index=result["feature_index"],
                geometry_type=result["geometry_type"],
                crs=result["crs"],
                measurement_type=result["measurement_type"],
                measurement_value=result["measurement_value"],
                properties=json.dumps(result["properties"])
            )

            db.add(measurement)

        uploaded_file.status = "processed"

        db.commit()

    except Exception as error:

        db.rollback()

        uploaded_file.status = "failed"
        db.commit()

        if saved_path.exists():
            saved_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=f"Unable to process geospatial file: {str(error)}"
        )

    return {
        "id": uploaded_file.id,
        "filename": uploaded_file.filename,
        "status": uploaded_file.status,
        "feature_count": len(measurements)
    }


@app.get("/api/files/{file_id}/")
def get_file(
    file_id: int,
    db: Session = Depends(get_db)
):

    uploaded_file = db.get(UploadedFile, file_id)

    if not uploaded_file:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    feature_count = (
        db.query(Measurement)
        .filter(Measurement.file_id == file_id)
        .count()
    )

    return {
        "id": uploaded_file.id,
        "filename": uploaded_file.filename,
        "status": uploaded_file.status,
        "feature_count": feature_count
    }


@app.get("/api/files/{file_id}/measurements/")
def get_file_measurements(
    file_id: int,
    db: Session = Depends(get_db)
):

    uploaded_file = db.get(UploadedFile, file_id)

    if not uploaded_file:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    measurements = (
        db.query(Measurement)
        .filter(Measurement.file_id == file_id)
        .all()
    )

    response_measurements = []

    for measurement in measurements:

        response_measurements.append({
            "feature_index": measurement.feature_index,
            "geometry_type": measurement.geometry_type,
            "crs": measurement.crs,
            "measurement_type": measurement.measurement_type,
            "measurement_value": measurement.measurement_value,
            "properties": json.loads(measurement.properties)
            if measurement.properties
            else {}
        })

    return {
        "file_id": uploaded_file.id,
        "filename": uploaded_file.filename,
        "measurements": response_measurements
    }