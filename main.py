import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Listing

app = FastAPI(title="Secondhand Marketplace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateListingResponse(BaseModel):
    id: str
    message: str


@app.get("/")
def read_root():
    return {"message": "Secondhand Marketplace Backend läuft"}


@app.get("/api/categories")
def categories():
    return {
        "categories": [
            "Möbel",
            "Kleidung",
            "Elektronik",
            "Haushalt",
            "Sport & Freizeit",
            "Kinder & Baby",
            "Bücher",
            "Spiele & Konsolen",
            "Autos & Fahrräder",
            "Sonstiges",
        ],
        "conditions": ["Neu", "Wie neu", "Gut", "Okay", "Gebraucht"],
        "delivery": ["Abholung", "Versand", "Treffen"],
        "currencies": ["EUR", "CHF", "USD"],
    }


@app.post("/api/listings", response_model=CreateListingResponse)
def create_listing(payload: Listing):
    listing_id = create_document("listing", payload)
    return {"id": listing_id, "message": "Angebot erfolgreich erstellt"}


@app.get("/api/listings")
def list_listings(
    q: Optional[str] = Query(None, description="Suchbegriff"),
    category: Optional[str] = None,
    condition: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    limit: int = Query(24, ge=1, le=100),
):
    if db is None:
        raise HTTPException(status_code=500, detail="Datenbank nicht verfügbar")

    filter_q = {}
    if q:
        filter_q["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}},
        ]
    if category:
        filter_q["category"] = category
    if condition:
        filter_q["condition"] = condition
    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = float(min_price)
    if max_price is not None:
        price_filter["$lte"] = float(max_price)
    if price_filter:
        filter_q["price"] = price_filter

    cursor = db["listing"].find(filter_q).sort("created_at", -1).limit(int(limit))
    results = []
    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        results.append(doc)
    return {"items": results, "count": len(results)}


@app.get("/api/listings/{listing_id}")
def get_listing(listing_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Datenbank nicht verfügbar")
    try:
        obj_id = ObjectId(listing_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")

    doc = db["listing"].find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    doc["id"] = str(doc.pop("_id"))
    return doc


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
