import json
import re
from collections import defaultdict
from difflib import SequenceMatcher
from collections import defaultdict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from fastapi_app.rag.validator import _normalize, is_valid_mcq

def docs_to_text(docs, max_chars=4000):
    """
    Convert LangChain documents into a single text block.
    Safely limits size to avoid token explosion.
    """
    text = ""
    for d in docs:
        if not hasattr(d, "page_content"):
            continue

        chunk = d.page_content.strip()
        if not chunk:
            continue

        if len(text) + len(chunk) > max_chars:
            break

        text += chunk + "\n\n"

    return text.strip()


def group_docs_by_source(docs):
    source_map = defaultdict(list)

    for d in docs:
        source_id = d.metadata.get("source", "unknown")
        source_map[source_id].append(d)

    return source_map


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _extract_json(text: str):
    if not text:
        return None

    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\[\s*{.*}\s*\]", text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def generate_questions(vector_store, num_questions=5):

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": max(40, num_questions * 8),
            "fetch_k": 200,
            "lambda_mult": 0.3
        }
    )

    docs = retriever.invoke(
        "Key concepts and topics explained across ALL lectures and videos"
    )

    if not docs:
        return []

    source_map = group_docs_by_source(docs)
    sources = list(source_map.keys())
    source_count = len(sources)

    if source_count == 0:
        return []

    base = num_questions // source_count
    extra = num_questions % source_count

    distribution = [
        base + (1 if i < extra else 0)
        for i in range(source_count)
    ]

    llm = ChatOpenAI(
        model="gpt-5-nano",
        temperature=0,
        request_timeout=25
    )
    
    prompt = PromptTemplate.from_template("""
You are an expert instructor.

TASK:
Generate EXACTLY {num} UNIQUE multiple-choice questions.

MANDATORY DIVERSITY RULES:
- EACH question MUST test a DIFFERENT concept or topic
- NEVER generate two questions from the same idea
- Spread questions across all topics in the context

CRITICAL RULES:
- EXACTLY 4 options: A, B, C, D
- Only ONE correct answer
- Options must be semantically DISTINCT
- No duplicated or similar questions
- No repeated or paraphrased options
- Incorrect options must be plausible but clearly wrong
- NO explanations
- NO markdown
- OUTPUT ONLY valid JSON
- Use DOUBLE QUOTES only

FORMAT:
[
  {{
    "question": "...",
    "options": {{
      "A": "...",
      "B": "...",
      "C": "...",
      "D": "..."
    }},
    "correct_answer": "A"
  }}
]

Context:
{context}
""")

    chain = prompt | llm | StrOutputParser()

    collected = []
    seen = set()

    for source, need in zip(sources, distribution):
        if need <= 0:
            continue

        context = docs_to_text(source_map[source], max_chars=3500)

        attempts = 0
        while need > 0 and attempts < 4:
            attempts += 1

            raw = chain.invoke({
                "context": context,
                "num": need
            })

            parsed = _extract_json(raw)
            if not isinstance(parsed, list):
                continue

            for q in parsed:
                if not is_valid_mcq(q):
                    continue

                q_text = q["question"].strip()
                norm_q = _normalize(q_text)

                if norm_q in seen:
                    continue

                if any(
                    similarity(q_text, ex["question"]) > 0.80
                    for ex in collected
                ):
                    continue

                seen.add(norm_q)
                collected.append(q)
                need -= 1

                if len(collected) == num_questions:
                    return collected

    remaining = num_questions - len(collected)
    if remaining > 0:
        context = docs_to_text(docs, max_chars=4500)

        raw = chain.invoke({
            "context": context,
            "num": remaining
        })

        parsed = _extract_json(raw) or []
        for q in parsed:
            q_text = q["question"].strip()
            norm_q = _normalize(q_text)

            if norm_q in seen:
                continue

            if any(
                similarity(q_text, ex["question"]) > 0.80
                for ex in collected
            ):
                continue

            collected.append(q)
            seen.add(norm_q)

            if len(collected) == num_questions:
                break

    return collected
