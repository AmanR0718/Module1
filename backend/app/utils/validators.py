"""
backend/app/utils/validators.py
Validation utilities for NRC numbers, phone numbers, emails, GPS, age, and land size.
Used across the Zambian Farmer Support System for data quality enforcement.
"""

import re
from typing import Optional
from datetime import date
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# ============================================================
# 🔹 PHONE NUMBER VALIDATION
# ============================================================
def validate_phone_number(phone: str, raise_on_fail: bool = False) -> bool:
    """
    Validate Zambian phone number format.
    Accepted formats: +260971234567, +260-97-1234567
    """
    try:
        phone = phone.strip()
        pattern = r"^\+260[- ]?\d{2}[- ]?\d{6,7}$"
        if not re.match(pattern, phone):
            if raise_on_fail:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid phone number format: {phone}. Expected +260XXXXXXXXX",
                )
            return False
        return True
    except Exception as e:
        logger.error(f"Phone validation error: {e}")
        return False


# ============================================================
# 🔹 NRC VALIDATION
# ============================================================
def validate_nrc_number(nrc: str, raise_on_fail: bool = False) -> bool:
    """
    Validate Zambian NRC format (e.g., 123456/12/1).
    """
    try:
        nrc = nrc.strip()
        pattern = r"^\d{6}/\d{2}/\d{1}$"
        if not re.match(pattern, nrc):
            if raise_on_fail:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid NRC format: {nrc}. Expected format: 123456/12/1",
                )
            return False
        return True
    except Exception as e:
        logger.error(f"NRC validation error: {e}")
        return False


# ============================================================
# 🔹 EMAIL VALIDATION
# ============================================================
def validate_email(email: str, raise_on_fail: bool = False) -> bool:
    """
    Validate email address format.
    """
    try:
        email = email.strip()
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            if raise_on_fail:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid email format: {email}",
                )
            return False
        return True
    except Exception as e:
        logger.error(f"Email validation error: {e}")
        return False


# ============================================================
# 🔹 GPS COORDINATES VALIDATION
# ============================================================
def validate_gps_coordinates(lat: float, lon: float, raise_on_fail: bool = False) -> bool:
    """
    Validate if GPS coordinates are within Zambia’s geographical boundaries.
    Approximate bounds:
        Latitude: -18.5 to -8.0
        Longitude: 21.5 to 34.0
    """
    try:
        lat, lon = float(lat), float(lon)
        if not (-18.5 <= lat <= -8.0 and 21.5 <= lon <= 34.0):
            if raise_on_fail:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Coordinates ({lat}, {lon}) out of Zambia bounds.",
                )
            return False
        return True
    except Exception as e:
        logger.error(f"GPS validation error: {e}")
        return False


# ============================================================
# 🔹 AGE VALIDATION
# ============================================================
def validate_age(dob: date, min_age: int = 18, raise_on_fail: bool = False) -> bool:
    """
    Validate that the farmer is at least `min_age` years old.
    """
    try:
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        valid = age >= min_age
        if not valid and raise_on_fail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Farmer must be at least {min_age} years old. Provided DOB: {dob}",
            )
        return valid
    except Exception as e:
        logger.error(f"Age validation error: {e}")
        return False


# ============================================================
# 🔹 LAND AREA VALIDATION
# ============================================================
def validate_land_area(
    area: float,
    min_area: float = 0.1,
    max_area: float = 1000.0,
    raise_on_fail: bool = False,
) -> bool:
    """
    Validate that the land area is within the allowed range (in hectares).
    Default range: 0.1 to 1000 hectares.
    """
    try:
        area = float(area)
        if not (min_area <= area <= max_area):
            if raise_on_fail:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid land area: {area} ha. Allowed range: {min_area}-{max_area} ha.",
                )
            return False
        return True
    except Exception as e:
        logger.error(f"Land area validation error: {e}")
        return False
