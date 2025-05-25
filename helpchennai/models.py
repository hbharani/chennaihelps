from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, validator

# Based on SERVICES in forms.py
# Not strictly a Pydantic model, but useful constants
SERVICES_LIST = ['Select', 'Shelter', 'Food', 'Transport', 'Clothes', 'All']

class GeoPoint(BaseModel):
    # It seems coordinates are expected as [lng, lat]
    lat: float
    lng: float

class BaseHelpModel(BaseModel):
    name: str
    phone: str
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    noofpeople: str # Example: '1', '2', '>20'
    notes: Optional[str] = None
    lat: float
    lng: float

class RequestHelpForm(BaseHelpModel):
    # Renamed from 'request' to 'request_service' to avoid conflicts
    # and for clarity
    request_service: str

    @validator('request_service')
    def service_must_be_valid(cls, value):
        if value not in SERVICES_LIST:
            raise ValueError(f"Service must be one of {SERVICES_LIST}")
        if value == 'Select':
            raise ValueError("A valid service must be selected")
        return value

class OfferHelpForm(BaseHelpModel):
    # Renamed from 'offer' to 'offer_service'
    offer_service: str

    @validator('offer_service')
    def service_must_be_valid(cls, value):
        if value not in SERVICES_LIST:
            raise ValueError(f"Service must be one of {SERVICES_LIST}")
        if value == 'Select':
            raise ValueError("A valid service must be selected")
        return value

# For getPoints endpoint
# The request body for getPoints is what json.loads(request.data) produces.
# The Flask code is: boundingBox = [json.loads(request.data)]
# The MongoDB query uses: "coordinates": boundingBox
# A GeoJSON polygon's coordinates are like: [[ [lng1, lat1], [lng2, lat2], ... ]]
# So, json.loads(request.data) should produce List[List[float]] representing one ring.
class BoundingBoxCoordinates(BaseModel):
    # A list of [lng, lat] pairs forming a polygon ring
    coordinates: List[List[float]]

    @validator('coordinates')
    def polygon_must_have_at_least_3_points_and_be_closed(cls, v):
        if len(v) < 4: # GeoJSON spec: min 4 points for a linear ring (first and last are the same)
            raise ValueError('A polygon ring must have at least 4 points.')
        if v[0] != v[-1]:
            raise ValueError('A polygon ring must be closed (first and last points must be the same).')
        for point in v:
            if not (isinstance(point, list) and len(point) == 2 and all(isinstance(coord, (int, float)) for coord in point)):
                raise ValueError('Each point in the polygon ring must be a list of two numbers (longitude, latitude).')
        return v


class PointProperties(BaseModel):
    type: str # "Requesting" or "Offering"
    id: str

class Geometry(BaseModel):
    type: str = "Point"
    coordinates: List[float] # [longitude, latitude]

class Feature(BaseModel):
    type: str = "Feature"
    geometry: Geometry
    properties: PointProperties

class FeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Feature]

# For the data passed to the show-info.html template
class InfoDetails(BaseModel):
    name: str
    phone: str
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    noofpeople: str
    type: str # "Requesting" or "Offering"
    service: str
    id: str
    notes: Optional[str] = None
