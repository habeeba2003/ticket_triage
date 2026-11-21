# Ticket Triage

An API that triages customer support tickets. Send it a ticket and it returns a category, a priority, a one-sentence summary and a **draft** reply, together with the most similar past tickets it used as evidence.

Built with **Python, FastAPI, NLP (sentence embeddings) and an LLM (Groq API)**.

> This is a learning and portfolio project. It runs on a small sample dataset of 20 tickets, and the replies it writes are drafts for a human to review.

## How it works

```
Client (Swagger UI)
      |  POST /tickets/analyze  {"text": "..."}
      v
FastAPI + Pydantic        validates the request (5 to 2000 characters)
      |
Embeddings (local)        sentence-transformers turns the text into a 384-number vector
      |
Similarity search         cosine similarity against the stored sample tickets, top 3 kept
      |
LLM (Groq API)            prompt = new ticket + similar tickets, JSON mode
      |
Pydantic validation       category and priority must be allowed values
      v
JSON response             analysis + similar tickets
```

**Why both NLP and an LLM?** Embeddings are fast, free and run locally, so they find relevant past tickets. The LLM then reads the new ticket together with those examples and writes the analysis. Giving it real examples from the data keeps its answer grounded. This is a simplified version of the retrieval-augmented generation (RAG) pattern.

## Features

- Semantic search: "unable to sign in" matches "I can't log in" even though the words differ
- Structured LLM output: JSON mode plus Pydantic validation, so `category` and `priority` can only be allowed values
- Clean error handling: if the LLM fails, the API returns a 502 with a short message and logs the details
- Text preprocessing endpoint that keeps negations ("not", "isn't") so the meaning is not lost
- Automated tests (pytest) that mock the LLM, so they are fast and free

## Tech stack

| Area | Tool |
|---|---|
| Web framework | FastAPI, served by Uvicorn |
| Data validation | Pydantic |
| Text preprocessing | NLTK (stop words, WordNet lemmatizer) |
| Embeddings | sentence-transformers, model `all-MiniLM-L6-v2` (runs locally) |
| LLM | Groq API (model name set in `.env`) |
| Configuration | python-dotenv |
| Tests | pytest, FastAPI TestClient |

## Project structure

```
ticket_triage/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app and endpoints
│   ├── schemas.py       # Pydantic request and response models
│   ├── nlp.py           # text cleaning, tokenizing, lemmatizing
│   ├── embeddings.py    # embeddings, similarity search, category vote
│   ├── llm.py           # prompt, Groq call, JSON parsing and validation
│   └── data_loader.py   # loads the sample tickets
├── data/
│   └── sample_tickets.json
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

You need Python 3.10 or newer and a free Groq API key from console.groq.com.

```bash
git clone https://github.com/habeeba2003/ticket_triage.git
cd ticket_triage

python -m venv venv
# Windows (cmd):         venv\Scripts\activate.bat
# Windows (PowerShell):  venv\Scripts\Activate.ps1
# macOS / Linux:         source venv/bin/activate

pip install -r requirements.txt
```

Create a file named `.env` in the project root (copy `.env.example`) and add your key:

```
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Never commit `.env`. It is listed in `.gitignore`. If a model name is no longer available, replace `GROQ_MODEL` with a current chat model from the Groq console.

## Run

```bash
uvicorn app.main:app --reload
```

The first start is slow: it downloads the embedding model (about 90 MB) and the NLTK word lists, then loads them. Wait for `Application startup complete.`

Open **http://127.0.0.1:8000/docs** for the interactive Swagger UI.

## API endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | Checks that the server is alive |
| POST | `/tickets/preprocess` | Returns the cleaned text and tokens |
| POST | `/tickets/similar` | Returns the 3 most similar sample tickets with scores |
| POST | `/tickets/category` | Suggests a category by a weighted vote of the nearest tickets |
| POST | `/tickets/analyze` | Full pipeline: similar tickets, then LLM analysis |

### Example

Request to `POST /tickets/analyze`:

```json
{ "text": "my card was charged two times" }
```

Response (shortened):

```json
{
  "query": "my card was charged two times",
  "analysis": {
    "category": "billing",
    "priority": "high",
    "summary": "Card was charged twice.",
    "suggested_reply": "We're sorry to hear your card was charged twice. Could you please provide the transaction date, amount, and any order or reference number so we can investigate further?"
  },
  "similar_tickets": [
    {
      "id": 4,
      "text": "I was charged twice for my subscription this month. Please check and refund the extra payment.",
      "category": "billing",
      "priority": "high",
      "score": 0.581
    }
  ]
}
```

LLM output varies from run to run, so your wording will differ.

### Errors

| Code | Meaning |
|---|---|
| 422 | The request body is invalid, for example text shorter than 5 or longer than 2000 characters |
| 502 | The LLM service failed or returned unusable output twice |

## Tests

```bash
python -m pytest -v
```

The tests replace the LLM with a fake answer, so they do not use the network or your API quota.

## Design decisions

- **Local embeddings, hosted LLM.** The embedding model is small and free to run locally. A useful LLM is far too large for a typical laptop, so it is called through an API.
- **Embed the original text, not the preprocessed tokens.** Embedding models are trained on natural sentences, so removing stop words would remove context.
- **JSON mode plus Pydantic.** JSON mode gives parseable JSON but does not guarantee the shape, so every reply is validated before it is used.
- **Reply is a draft.** Prompt instructions reduce, but do not remove, the chance that the model promises something the company has not approved.

## Limitations and next steps

- The dataset has only 20 sample tickets, so similarity results are limited by that small set.
- Ticket data is loaded from a JSON file and kept in memory. A real system would use a database and a vector index.
- There is no authentication or rate limiting on the API.
- A similarity threshold could mark off-topic text (for example, a weather question) as "unknown" before calling the LLM.
- Possible additions: a simple web page for pasting tickets, a larger labelled dataset, and an evaluation script that measures category accuracy.

## What I learned building this

The bugs taught me more than the features did:

- **Stop-word lists can flip meaning.** NLTK's list removes "not" and contractions like "isn't", so "my payment isn't showing" lost its negation. I now protect them, and the preprocessing endpoint shows the result.
- **A test warning exposed a silent typo.** `max_leangth` instead of `max_length` meant the 2000-character limit was never enforced. A test for oversized text now fails if the limit ever disappears.
- **Vote share is a misleading confidence.** An off-topic question ("what is the weather today") was assigned the shipping category with 0.883 vote share, even though its best similarity score was only 0.22. Raw similarity is the better signal.
- **LLM output needs validation and review.** Even with an instruction not to promise refunds, one draft reply still did. That is why replies are drafts and every answer is checked against a schema.
- **Read errors from the bottom.** The last line of a traceback names the problem, and the last file path that is yours shows where.


## About the author

Hi, I'm **Habeeba**, and I built this project to learn how NLP and an LLM work together inside a real API.

Questions, ideas and bug reports are welcome. Open an issue on this repository.
