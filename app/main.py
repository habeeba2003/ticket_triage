from app.schemas import TicketRequest, TicketEcho
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