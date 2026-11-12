from app import nlp, embeddings
from app.schemas import (
    TicketRequest, 
    TicketEcho, 
    PreprocessResponse,
    SimilarResponse,
    CategoryResponse,
)

from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def welcome():
    return {"message": "Welcome to Ticket Triage"}

@app.get("/about")
def project():
    return {"project": "Ticket Triage"}

@app.post("/tickets/analyze", response_model=TicketEcho)
def analyze_ticket(ticket: TicketRequest):
    return TicketEcho(
        received_text=ticket.text,
        customer_id=ticket.customer_id,
        word_count=len(ticket.text.split()),
    )

@app.post("/tickets/preprocess", response_model=PreprocessResponse)
def preprocess_ticket(ticket: TicketRequest):
    tokens = nlp.preprocess(ticket.text)
    return PreprocessResponse(
        original=ticket.text,
        cleaned=nlp.clean_text(ticket.text),
        tokens=tokens,
        token_count=len(tokens),
    )

@app.post("/tickets/similar", response_model=SimilarResponse)
def similar_tickets(ticket: TicketRequest):
    results = embeddings.find_similar(ticket.text, top_k=3)
    return SimilarResponse(query=ticket.text, results=results)

@app.post("/tickets/category", response_model=CategoryResponse)
def suggest_ticket_category(ticket: TicketRequest):
    result = embeddings.suggest_category(ticket.text)
    return CategoryResponse(
        query=ticket.text,
        suggested_category=result["category"],
        confidence=result["confidence"],
        matches=result["matches"],
    )