import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Movie

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Movies API is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
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
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# Request models for creating and updating movies
class MovieCreate(Movie):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    genres: Optional[List[str]] = None
    rating: Optional[float] = None
    poster_url: Optional[str] = None
    description: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[List[str]] = None

# Helpers

def serialize_movie(doc):
    return {
        "id": str(doc.get("_id")),
        "title": doc.get("title"),
        "year": doc.get("year"),
        "genres": doc.get("genres", []),
        "rating": doc.get("rating"),
        "poster_url": doc.get("poster_url"),
        "description": doc.get("description"),
        "director": doc.get("director"),
        "cast": doc.get("cast", []),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }

MOVIE_COLLECTION = "movie"

@app.get("/api/movies", response_model=List[dict])
def list_movies(q: Optional[str] = None, genre: Optional[str] = None):
    filter_query = {}
    if q:
        filter_query["title"] = {"$regex": q, "$options": "i"}
    if genre:
        filter_query["genres"] = {"$in": [genre]}
    docs = get_documents(MOVIE_COLLECTION, filter_query)
    return [serialize_movie(d) for d in docs]

@app.post("/api/movies", status_code=201)
def create_movie(movie: MovieCreate):
    movie_id = create_document(MOVIE_COLLECTION, movie)
    created = db[MOVIE_COLLECTION].find_one({"_id": ObjectId(movie_id)})
    return serialize_movie(created)

@app.get("/api/movies/{movie_id}")
def get_movie(movie_id: str):
    try:
        oid = ObjectId(movie_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
    doc = db[MOVIE_COLLECTION].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Movie not found")
    return serialize_movie(doc)

@app.put("/api/movies/{movie_id}")
def update_movie(movie_id: str, payload: MovieUpdate):
    try:
        oid = ObjectId(movie_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    update_data["updated_at"] = __import__("datetime").datetime.utcnow()

    result = db[MOVIE_COLLECTION].update_one({"_id": oid}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found")

    doc = db[MOVIE_COLLECTION].find_one({"_id": oid})
    return serialize_movie(doc)

@app.delete("/api/movies/{movie_id}", status_code=204)
def delete_movie(movie_id: str):
    try:
        oid = ObjectId(movie_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = db[MOVIE_COLLECTION].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"status": "deleted"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
