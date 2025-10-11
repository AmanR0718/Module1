import re
from typing import Optional
from datetime import date
from fastapi import HTTPException, status

def validate_phone_number(phone: str) -> bool:
    """Validate Zambian phone number format"""
    pattern = r'^\+260-?\d{2}-?\d{7}$'
    return bool(re.match(pattern, phone))

def validate_nrc_number(nrc: str) -> bool:
    """Validate Zambian NRC format (e.g., 123456/12/1)"""
    pattern = r'^\d{6}/\d{2}/\d{1}$'
    return bool(re.match(pattern, nrc))

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_gps_coordinates(lat: float, lon: float) -> bool:
    """Validate GPS coordinates are within Zambia bounds"""
    # Zambia approximate bounds
    if not (-18.5 <= lat <= -8.0):
        return False
    if not (21.5 <= lon <= 34.0):
        return False
    return True

def validate_age(dob: date, min_age: int = 18) -> bool:
    """Validate minimum age requirement"""
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age >= min_age

def validate_land_area(area: float, min_area: float = 0.1, max_area: float = 1000) -> bool:
    """Validate land area is within acceptable range"""
    return min_area <= area <= max_area
