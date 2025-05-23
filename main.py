import datetime # Keep existing imports if any
from fastapi import FastAPI, Request, Response, HTTPException, Depends # Added Request, Response, HTTPException, Depends
from pymongo import MongoClient, GEOSPHERE # Keep existing
from bson.objectid import ObjectId # Keep existing
import json # Keep existing
from typing import List # Added List

# Import Pydantic models (assuming they are in helpchennai.models)
from helpchennai.models import (
    RequestHelpForm, OfferHelpForm, BoundingBoxCoordinates,
    FeatureCollection, Feature, Geometry, PointProperties, InfoDetails
)

# For serving templates and static files
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse # Added HTMLResponse, RedirectResponse

# Initialize FastAPI app
app = FastAPI()

# Initialize MongoDB client (already there from previous step)
client = MongoClient()
db = client['Disaster_Help']
# Ensure 'chennai' collection has a 2dsphere index for geospatial queries
# This would typically be done once, but good to note.
# Example: db.chennai.create_index([("geometry", GEOSPHERE)])

# --- Setup Templates ---
templates = Jinja2Templates(directory="helpchennai/templates")

# --- Mount Static Files ---
# The path "/static" will serve files from "helpchennai/static" directory
app.mount("/static", StaticFiles(directory="helpchennai/static"), name="static")

# --- Migrated Routes ---

# Index route
@app.get("/", response_class=HTMLResponse)
@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    # Flask's render_template automatically includes the request context.
    # FastAPI's TemplateResponse requires the 'request: Request' to be passed explicitly.
    return templates.TemplateResponse("index.html", {"request": request})

# Placeholder for other routes (will be added incrementally)
@app.post("/getpoints", response_model=FeatureCollection)
async def get_points(bounding_box_coords: BoundingBoxCoordinates):
    # The request body is automatically parsed into BoundingBoxCoordinates
    # The Flask code was: boundingBox = [json.loads(request.data)]
    # Here, bounding_box_coords.coordinates is what json.loads(request.data) would have been.
    # The MongoDB query expects coordinates: [[ [lng1, lat1], [lng2, lat2], ... ]]
    # So, the 'coordinates' field of our Pydantic model BoundingBoxCoordinates
    # which is List[List[float]] (a single ring) needs to be wrapped in another list
    # for the $geoWithin query if it expects a MultiPolygon or a list of Polygons.
    # However, the original query was:
    # "geometry":{"$geoWithin": {"$geometry": {"type" : "Polygon" ,"coordinates": boundingBox}}}
    # where boundingBox was [json.loads(request.data)].
    # If json.loads(request.data) was [[lng1, lat1], [lng2, lat2], ...],
    # then mongo_query_coordinates = [bounding_box_coords.coordinates] is correct.

    mongo_query_coordinates = [bounding_box_coords.coordinates]

    chennai_collection = db["chennai"]
    parcel_features: List[Feature] = []

    # Ensure the collection exists and has data for testing
    # Example: if not chennai_collection.count_documents({}):
    #     print("Warning: 'chennai' collection is empty.")

    try:
        for doc in chennai_collection.find({
            "geometry": {
                "$geoWithin": {
                    "$geometry": {
                        "type": "Polygon",
                        "coordinates": mongo_query_coordinates
                    }
                }
            },
            "satisfied": 0
        }):
            # Ensure the document structure matches expectations
            # print(f"Found document: {doc}") # For debugging
            
            # Safely access nested fields with defaults or checks
            doc_geometry = doc.get("geometry")
            doc_properties = doc.get("properties")
            
            if not doc_geometry or not doc_properties:
                # print(f"Skipping document with missing geometry or properties: {doc.get('_id')}")
                continue

            feature = Feature(
                geometry=Geometry(
                    type=doc_geometry.get("type", "Point"), # Default to point if not specified
                    coordinates=doc_geometry.get("coordinates", [])
                ),
                properties=PointProperties(
                    type=doc_properties.get("type", "Unknown"), # Default if not specified
                    id=str(doc["_id"])
                )
            )
            parcel_features.append(feature)
    except Exception as e:
        # print(f"Error during database query or processing: {e}") # For debugging
        # Consider re-raising or returning an HTTP error if appropriate
        raise HTTPException(status_code=500, detail="Error processing map points")

    return FeatureCollection(features=parcel_features)

@app.get("/requesthelp", response_class=HTMLResponse)
async def request_help_form(request: Request):
    # In Flask, a RequestHelp() form object was passed.
    # For FastAPI, we'll render the template. If the template needs
    # specific form field data (like select choices), we might need to pass them.
    # For now, let's assume the template can render without a complex form object.
    # If `forms.py` defined choices (e.g., SERVICES), these might need to be
    # passed to the template context if the template expects them.
    # from helpchennai.forms import SERVICES as services_choices # Example
    from helpchennai.models import SERVICES_LIST # Using from models.py

    return templates.TemplateResponse("request-help.html", {
        "request": request,
        "services_choices": SERVICES_LIST, # Pass choices to the template
        "form_action_url": "/uploadrequest" # Explicitly define form action URL
    })

@app.get("/offerhelp", response_class=HTMLResponse)
async def offer_help_form(request: Request):
    # Similar to request_help_form, pass necessary data to the template.
    # from helpchennai.forms import SERVICES as services_choices # Example
    from helpchennai.models import SERVICES_LIST # Using from models.py

    return templates.TemplateResponse("offer-help.html", {
        "request": request,
        "services_choices": SERVICES_LIST, # Pass choices to the template
        "form_action_url": "/uploadoffer" # Explicitly define form action URL
    })

@app.post("/uploadrequest")
async def upload_request(request: Request, form_data: RequestHelpForm = Depends()):
    # FastAPI's Depends() with the Pydantic model will parse and validate form data.
    # If validation fails, FastAPI automatically returns a 422 error.
    # This replaces form.validate_on_submit() from Flask.

    chennai_collection = db["chennai"]
    
    document = {
        "type": "Feature",
        "satisfied": 0,
        "geometry": {
            "type": "Point",
            "coordinates": [form_data.lng, form_data.lat] # Order: Lng, Lat for GeoJSON
        },
        "properties": {
            "name": form_data.name,
            "phone": form_data.phone,
            "address": form_data.address,
            "email": form_data.email,
            "noofpeople": form_data.noofpeople,
            "service": form_data.request_service, # Using the Pydantic model field name
            "notes": form_data.notes,
            "type": "Requesting"
        },
        "timestamp": datetime.datetime.now()
    }

    try:
        chennai_collection.insert_one(document)
        # Original Flask app returned "1" on success.
        # We can redirect to a success page or return a JSON confirmation.
        # For now, let's mimic the old behavior with a plain text response.
        return Response(content="1", media_type="text/plain")
    except Exception as e:
        # Log the error e
        raise HTTPException(status_code=500, detail=f"Failed to save request: {str(e)}")

@app.post("/uploadoffer")
async def upload_offer(request: Request, form_data: OfferHelpForm = Depends()):
    # Similar to upload_request, using OfferHelpForm Pydantic model
    chennai_collection = db["chennai"]

    document = {
        "type": "Feature",
        "satisfied": 0,
        "geometry": {
            "type": "Point",
            "coordinates": [form_data.lng, form_data.lat] # Order: Lng, Lat for GeoJSON
        },
        "properties": {
            "name": form_data.name,
            "phone": form_data.phone,
            "address": form_data.address,
            "email": form_data.email,
            "noofpeople": form_data.noofpeople,
            "service": form_data.offer_service, # Using the Pydantic model field name
            "notes": form_data.notes,
            "type": "Offering"
        },
        "timestamp": datetime.datetime.now()
    }

    try:
        chennai_collection.insert_one(document)
        return Response(content="1", media_type="text/plain")
    except Exception as e:
        # Log the error e
        raise HTTPException(status_code=500, detail=f"Failed to save offer: {str(e)}")

@app.get("/showinfo", response_class=HTMLResponse)
async def show_info(request: Request, id: str): # id is a query parameter
    chennai_collection = db["chennai"]
    
    if not id:
        raise HTTPException(status_code=400, detail="ID parameter is missing")

    try:
        object_id = ObjectId(id)
    except Exception: # Covers InvalidId from bson.errors
        raise HTTPException(status_code=400, detail="Invalid ID format")

    document = chennai_collection.find_one({'_id': object_id})

    if not document:
        raise HTTPException(status_code=404, detail="Information not found")

    # Prepare data for the template, similar to original Flask app
    # Using the InfoDetails Pydantic model for structuring is also an option here,
    # but we can stick to passing individual items as per original if templates expect that.
    
    doc_properties = document.get("properties", {})
    
    template_data = {
        "request": request,
        "name": doc_properties.get("name"),
        "phone": doc_properties.get("phone"),
        "address": doc_properties.get("address", ""), # Default to empty string if not present
        "email": doc_properties.get("email"),
        "noofpeople": doc_properties.get("noofpeople"),
        "type": doc_properties.get("type"),
        "service": doc_properties.get("service"),
        "id": str(document["_id"]),
        "notes": doc_properties.get("notes", "") # Default to empty string if not present
    }
    
    # Validate with Pydantic model before sending to template for consistency (optional but good)
    try:
        # We need to adjust template_data to match InfoDetails if we want to validate it.
        # InfoDetails expects 'request' to not be part of its fields.
        validation_data = template_data.copy()
        validation_data.pop("request", None) # Remove 'request' if present
        InfoDetails(**validation_data) # This is just for validation
    except Exception as e:
        # Log this validation error, it means DB data might not match InfoDetails model
        # print(f"Data validation error for show_info: {e}")
        # Depending on strictness, could raise 500 or proceed with unvalidated data
        pass # For now, proceed even if validation fails, to match original behavior closely

    return templates.TemplateResponse("show-info.html", template_data)
