import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from groq import Groq

from validator import parse_and_validate

load_dotenv()

MAX_ATTEMPTS = 3
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

SYSTEM_PROMPT = """You extract structured data from text.
Return ONLY a JSON object with exactly these keys:
- "name": string (required)
- "age": integer or null
- "skills": array of strings (empty array if none)
- "email": string or null

Rules:
- Use only information stated in the text. Never invent or guess details.
- If a value is missing, use null (or [] for skills).
- Normalize skill capitalization (e.g. "machine learning" -> "Machine Learning").
- No extra keys, no commentary, no markdown fences."""


@dataclass
class ExtractionResult:
    ok: bool
    data: dict | None = None
    errors: list[str] = field(default_factory=list)
    attempts: int = 0


def call_llm(messages: list[dict]) -> str:
    client = Groq()  # GROQ_API_KEY .env theke nibe
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        temperature=0,
    )
    return resp.choices[0].message.content


def extract(text: str, llm=call_llm, max_attempts: int = MAX_ATTEMPTS) -> ExtractionResult:
    if not text or not text.strip():
        return ExtractionResult(ok=False, errors=["Input text is empty."])

    messages = [{"role": "user", "content": f"Text:\n{text}"}]
    errors: list[str] = []

    for attempt in range(1, max_attempts + 1):
        try:
            raw = llm(messages)
        except Exception as exc:  # API fail / rate limit hole loop kore na
            return ExtractionResult(
                ok=False, errors=[f"LLM call failed: {exc}"], attempts=attempt
            )

        profile, errors = parse_and_validate(raw)
        if profile is not None:
            return ExtractionResult(
                ok=True, data=profile.model_dump(mode="json"), attempts=attempt
            )

        # Fail hole error shoho abar LLM ke pathai
        messages = messages + [
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": "Your previous output was invalid:\n- "
                + "\n- ".join(errors)
                + "\nReturn corrected JSON only.",
            },
        ]

    return ExtractionResult(ok=False, errors=errors, attempts=max_attempts)