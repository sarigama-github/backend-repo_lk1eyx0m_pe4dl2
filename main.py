import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime

from database import db, create_document, get_documents
from schemas import ContactMessage, NewsletterSubscriber, BlogPost, CaseStudy

app = FastAPI(title="AVESSAS API", description="Backend para o website AVESSAS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AVESSAS Backend ativo"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response

# ---------------------- Models for requests ----------------------

class ContactRequest(ContactMessage):
    pass

class NewsletterRequest(NewsletterSubscriber):
    pass

# ---------------------- Content: Blog ---------------------------

@app.get("/blog", response_model=List[BlogPost])
def list_blog_posts(limit: int = 20):
    try:
        docs = get_documents("blogpost", {}, limit)
        # Convert Mongo docs to Pydantic dicts
        result: List[BlogPost] = []
        for d in docs:
            d.pop("_id", None)
            result.append(BlogPost(**d))
        return result
    except Exception:
        # Return some default demo posts if DB not available
        demo = [
            BlogPost(
                title="Farto de conversas desagradáveis…",
                slug="farto-de-conversas-desagradaveis",
                summary="Porque a coragem para enfrentar o problema certo muda resultados.",
                content="Texto breve de demonstração.",
                tags=["lideranca", "gestao"],
            ),
            BlogPost(
                title="Até as crianças vendem melhor do que tu!",
                slug="criancas-vendem-melhor",
                summary="Provocação certa para desbloquear equipas comerciais.",
                content="Texto breve de demonstração.",
                tags=["vendas", "marketing"],
            ),
        ]
        return demo

# ---------------------- Content: Case Studies -------------------

@app.get("/cases", response_model=List[CaseStudy])
def list_cases(limit: int = 12):
    try:
        docs = get_documents("casestudy", {}, limit)
        res: List[CaseStudy] = []
        for d in docs:
            d.pop("_id", None)
            res.append(CaseStudy(**d))
        return res
    except Exception:
        return []

# ---------------------- Lead capture ----------------------------

@app.post("/contact")
def send_contact(payload: ContactRequest):
    try:
        contact_id = create_document("contactmessage", payload)
        return {"status": "ok", "id": contact_id}
    except Exception as e:
        # Graceful fallback even if DB unavailable
        return {"status": "queued", "reason": str(e)[:120]}

@app.post("/newsletter")
def subscribe_newsletter(payload: NewsletterRequest):
    try:
        sub_id = create_document("newslettersubscriber", payload)
        return {"status": "ok", "id": sub_id}
    except Exception as e:
        return {"status": "queued", "reason": str(e)[:120]}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
