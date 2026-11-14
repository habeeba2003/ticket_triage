SYSTEM_PROMPT = """You are a support ticket triage assistant.
Read the new ticket and the similar past tickets given as context. 
Reply with ONE JSON object and nothing else, with exactly these keys:
- "category": one of "billing", "login", "shipping", "technical", "unknown"
- "priority": one of "low", "medium", "high"
- "summary": one sentence describing the problem
- "suggested_reply": a polite reply of at most three sentences
Use "unknown" if the ticket is not a customer support issue.
Do not invent order numbers, refunds or company policies."""

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