import json
import os

from dotenv import load_dotenv
from groq import Groq, APIConnectionError, APIStatusError
from pydantic import ValidationError

from app.schemas import LLMAnalysis

load_dotenv()

_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

SYSTEM_PROMPT = """You are a support ticket triage assistant.
Read the new ticket and the similar past tickets given as context. 
Reply with ONE JSON object and nothing else, with exactly these keys:
- "category": one of "billing", "login", "shipping", "technical", "unknown"
- "priority": one of "low", "medium", "high"
- "summary": one sentence describing the problem
- "suggested_reply": a polite reply of at most three sentences that acknowledges 
the issue and asks for any missing details, without promising refunds, 
credits or timelines."""

def build_prompt(ticket_text: str, similar: list[dict]) -> str:
    examples = "\n".join(
        f'- "{m["text"]}" (category: {m["category"]}, priority: {m["priority"]})'
        for m in similar
    )
    return (
        f"New ticket:\n{ticket_text}\n\n"
        f"Similar past tickets:\n{examples}\n\n"
        "Return the JSON object now."
    )

class LLMError(Exception):
    """Raised when the LLM cannot give a valid analysis."""


def analyze_with_llm(
    ticket_text: str, similar: list[dict], max_attempts: int = 2
) -> LLMAnalysis:
    prompt = build_prompt(ticket_text, similar)
    last_problem = "unknown problem"

    for attempt in range(1, max_attempts + 1):
        try:
            response = _client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
            return LLMAnalysis.model_validate(json.loads(raw))
        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            last_problem = f"attempt {attempt}: invalid model output ({exc})"
        except (APIConnectionError, APIStatusError) as exc:
            raise LLMError(f"Groq request failed: {exc}") from exc

    raise LLMError(f"No valid analysis. Last problem: {last_problem}")