from sentence_transformers import SentenceTransformer, util

from app.data_loader import load_tickets

MODEL_NAME = "all-MiniLM-L6-v2"

_model = SentenceTransformer(MODEL_NAME)
_tickets = load_tickets()
_ticket_embeddings = _model.encode([t["text"] for t in _tickets])


def find_similar(text: str, top_k: int = 3) -> list[dict]:
    query_embedding = _model.encode(text)
    scores = util.cos_sim(query_embedding, _ticket_embeddings)[0]
    ranked = sorted(
        zip(_tickets, scores.tolist()),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return [{**ticket, "score": round(score, 3)} for ticket, score in ranked[:top_k]]

def suggest_category(text: str, top_k: int = 5) -> dict:
    matches = find_similar(text, top_k=top_k)

    totals: dict[str, float] = {}
    for match in matches:
        category = match["category"]
        totals[category] = totals.get(category, 0.0) + match["score"]

    best = max(totals, key=totals.get)
    confidence = totals[best] / sum(totals.values())

    return {
        "category": best,
        "confidence": round(confidence, 3),
        "matches": matches,
    }