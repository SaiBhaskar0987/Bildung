import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

import re
from difflib import SequenceMatcher

def _normalize(text: str) -> str:
    """
    Aggressively normalize text to detect duplicates and near-duplicates.
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)   
    text = re.sub(r"\s+", " ", text)     
    return text

def _is_similar(a: str, b: str, threshold: float = 0.88) -> bool:
    """
    Detect near-duplicate strings using similarity ratio.
    """
    return SequenceMatcher(
        None,
        _normalize(a),
        _normalize(b)
    ).ratio() >= threshold

def is_valid_mcq(q: dict) -> bool:
    try:
        if not isinstance(q, dict):
            return False

        question = q.get("question")
        options = q.get("options")
        correct = q.get("correct_answer")

        if not isinstance(question, str) or len(question.strip()) < 8:
            return False

        if not isinstance(options, dict):
            return False

        required_keys = {"A", "B", "C", "D"}
        if set(options.keys()) != required_keys:
            return False

        if correct not in required_keys:
            return False

        norm_question = _normalize(question)

        normalized_options = {}
        for k, v in options.items():
            if not isinstance(v, str) or not v.strip():
                return False
            normalized_options[k] = _normalize(v)

        if not options[correct].strip():
            return False

        seen = set()
        for k, norm in normalized_options.items():
            if norm in seen:
                return False
            seen.add(norm)

        keys = list(normalized_options.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                if _is_similar(
                    normalized_options[keys[i]],
                    normalized_options[keys[j]]
                ):
                    return False

        for norm_opt in normalized_options.values():
            if _is_similar(norm_opt, norm_question, threshold=0.90):
                return False

        return True

    except Exception:
        return False


def trim_context(docs, max_chars=3000):
    """
    Reduce context size before sending to LLM.
    Keeps early chunks which are usually most relevant.
    """
    text = ""
    for d in docs:
        if len(text) >= max_chars:
            break
        text += d.page_content.strip() + "\n\n"
    return text.strip()

def validate_answer(vector_store, question: str, student_answer: str):
    """
    Validate a student's answer using ONLY retrieved context.
    Optimized + safe.
    """

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    docs = retriever.invoke(question)

    if not docs:
        return {
            "is_correct": False,
            "confidence": 0.0,
            "explanation": "No relevant material found for this question"
        }

    context = trim_context(docs, max_chars=3000)

    prompt = PromptTemplate.from_template(
        """
You are a strict evaluator.

Use ONLY the context below.
If the answer is not clearly supported by the context,
mark it as incorrect.

Context:
{context}

Question:
{question}

Student Answer:
{answer}

Respond ONLY in valid JSON:
{{
  "is_correct": true or false,
  "confidence": 0.0 to 1.0,
  "explanation": "short explanation"
}}
        """.strip()
    )

    llm = ChatOpenAI(
    model="gpt-4o-mini",  
    temperature=0,
    request_timeout=15
)

    chain = (
        prompt
        | llm
        | StrOutputParser()
    )

    result = chain.invoke({
        "context": context,
        "question": question,
        "answer": student_answer
    })

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {
            "is_correct": False,
            "confidence": 0.0,
            "explanation": "Model returned invalid JSON"
        }


def grounded_validate(vector_store, question: str, answer: str):
    """
    Extra safety layer:
    First ensures relevant content exists in vector store.
    """

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    docs = retriever.invoke(question)

    if not docs:
        return {
            "is_correct": False,
            "confidence": 0.0,
            "explanation": "Answer not found in provided material"
        }

    return validate_answer(vector_store, question, answer)

