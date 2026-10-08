from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String(255),
        nullable=False
    )

    file_type = Column(
        String(50),
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False,
        default="uploaded"
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_id = Column(
        Integer,
        ForeignKey("uploaded_files.id"),
        nullable=False
    )

    feature_index = Column(
        Integer,
        nullable=False
    )

    geometry_type = Column(
        String(50),
        nullable=False
    )

    crs = Column(
        String(100),
        nullable=True
    )

    measurement_type = Column(
        String(30),
        nullable=True
    )

    measurement_value = Column(
        Float,
        nullable=True
    )

    properties = Column(
        Text,
        nullable=True
    )