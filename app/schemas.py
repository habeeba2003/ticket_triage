# A schema is a description of what data should look like.

from pydantic import BaseModel, Field 

class TicketRequest(BaseModel):
    text: str = Field(min_length=5, max_leangth=2000)
    customer_id: int | None = None

class TicketEcho(BaseModel):
    received_text: str
    customer_id: int | None
    word_count: int

class PreprocessResponse(BaseModel):
    original: str
    cleaned: str
    tokens: list[str]
    token_count: int

class SimilarTicket(BaseModel):
    id: int
    text: str
    category: str
    priority: str
    score: float


class SimilarResponse(BaseModel):
    query: str
    results: list[SimilarTicket]