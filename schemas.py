"""
Database Schemas for AVESSAS site

Each Pydantic model maps to a MongoDB collection using the lowercase class name.
Examples:
- ContactMessage -> "contactmessage"
- BlogPost -> "blogpost"
- CaseStudy -> "casestudy"
- NewsletterSubscriber -> "newslettersubscriber"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# ---------------------- Core Collections ----------------------

class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, description="Nome do contacto")
    company: Optional[str] = Field(None, max_length=160, description="Empresa")
    email: EmailStr = Field(..., description="E-mail para contacto")
    message: str = Field(..., min_length=5, max_length=4000, description="Mensagem")
    subscribed: bool = Field(False, description="Aceitou newsletter")

class NewsletterSubscriber(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    source: str = Field("website", description="Origem da subscrição")

class BlogPost(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    slug: str = Field(..., min_length=3, max_length=220)
    summary: str = Field(..., min_length=10, max_length=400)
    content: str = Field(..., min_length=20)
    author: str = Field("Equipa AVESSAS")
    tags: List[str] = Field(default_factory=list)
    published_at: Optional[datetime] = None
    cover_image: Optional[str] = None

class CaseStudy(BaseModel):
    client: str = Field(..., min_length=2, max_length=140)
    sector: Optional[str] = None
    challenge: str
    approach: str
    impact: str
    metrics: Optional[List[str]] = Field(default_factory=list)
    logo: Optional[str] = None
