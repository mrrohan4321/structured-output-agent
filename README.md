# Structured Output Agent

Converts unstructured text into validated, predictable JSON. An LLM extracts the fields, a Pydantic schema checks them, and if validation fails the agent retries with the error feedback (maximum 3 attempts). If every attempt fails, it returns a clear error instead of pretending the output is valid.

**Live demo:** https://structured-output-agent-2czh8cwvyfsoaqlol3bhat.streamlit.app/

![App screenshot](screenshots/app.png)

## Features

- Extracts `name`, `age`, `skills` and `email` from free-form text
- Never invents missing details: unknown values become `null` (or `[]` for skills)
- Rejects unexpected fields and validates types and email format
- Bounded retry loop that feeds validation errors back to the LLM
- Handles empty input, malformed JSON and API failures without crashing
- Streamlit UI with a JSON result panel and a download button
- Automated tests that use a fake LLM, so no API key is needed to run them

## Pipeline

```
User input -> LLM extraction -> JSON parsing -> Schema validation -> Error-correction retry -> Valid JSON or clear failure
```

## Example

Input:

```
Hi, I'm Rahul Das. I'm 21 years old.
I know Python, SQL, and machine learning.
My email is rahul@example.com.
```

Output:

```json
{
  "name": "Rahul Das",
  "age": 21,
  "skills": ["Python", "SQL", "Machine Learning"],
  "email": "rahul@example.com"
}
```

Input with missing details:

```
My name is Priya.
```

Output:

```json
{
  "name": "Priya",
  "age": null,
  "skills": [],
  "email": null
}
```

## Tech stack

Python, Pydantic, Groq API, Streamlit, pytest

## Project structure

| File | Purpose |
|---|---|
| `schemas.py` | Pydantic `ContactProfile` model (extra fields forbidden) |
| `validator.py` | JSON parsing and schema validation helpers |
| `agent.py` | LLM call and bounded retry loop |
| `app.py` | Streamlit interface |
| `tests/test_agent.py` | Automated tests |

## Setup

```bash
git clone https://github.com/mrrohan4321/structured-output-agent.git
cd structured-output-agent
python -m venv .venv
.venv\Scripts\activate        # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GROQ_API_KEY=your-key-here
```

Get a free key at https://console.groq.com/keys. Never commit `.env` (it is already in `.gitignore`).

Optional: set `LLM_MODEL` in `.env` to use a different Groq model.

## Run

```bash
streamlit run app.py
```

## Test

```bash
pytest
```

Tests cover valid input, missing fields, invalid email, wrong types, extra fields, malformed JSON, empty input, retry recovery, retry exhaustion and API failure. They never call the real LLM.

## Deployment

The live demo runs on Streamlit Community Cloud. The API key is stored in the host's secrets settings, not in the repository.

## Known limitations

- The schema is fixed (`name`, `age`, `skills`, `email`). New fields require editing `schemas.py` and the prompt in `agent.py`.
- Validation checks structure, not truth. If the LLM extracts a wrong value that still fits the schema, it will pass.
- The live demo shares one free API key, so heavy use may hit rate limits.