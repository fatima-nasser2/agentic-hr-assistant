import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

_JUDGE_PROMPT = """\
You are an expert evaluator for an AI-powered HR assistant.
Assess the quality of the assistant's answer using only the retrieved context below.

## User Question
{question}

## Retrieved Context
{context}

## Assistant Answer
{answer}

Score the answer on three dimensions, each from 0.0 to 5.0:

**Groundedness** — Are all claims directly supported by the context?
  5 = fully grounded | 3 = mostly supported | 1 = several unsupported claims | 0 = contradicts context

**Relevance** — Does the answer directly address the question?
  5 = perfectly on-target | 3 = partially addresses it | 1 = barely related | 0 = off-topic

**Completeness** — Does the answer include all key information available in the context?
  5 = complete | 3 = main points covered, some gaps | 1 = important info missing | 0 = essentially useless

Respond with a JSON object with exactly these keys:
{{"groundedness": <number 0-5>, "relevance": <number 0-5>, "completeness": <number 0-5>, "reasoning": "<1-2 sentences>"}}\
"""


async def evaluate_answer(
    question: str,
    answer: str,
    documents: list,
    retrieval_source: str,
) -> dict | None:
    if not answer or not retrieval_source or retrieval_source == "unknown":
        return None

    if documents:
        parts = [
            doc.page_content if hasattr(doc, "page_content") else str(doc)
            for doc in documents
        ]
        context = "\n\n---\n\n".join(parts)
    else:
        context = "No context was retrieved."

    context = context[:3500]

    prompt = _JUDGE_PROMPT.format(
        question=question,
        context=context,
        answer=answer,
    )

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            timeout=10,
            max_retries=0,
            model_kwargs={"response_format": {"type": "json_object"}},
        )
        response = await llm.ainvoke([HumanMessage(content=prompt)])

        # content is a str in JSON mode
        content = response.content
        if isinstance(content, list):
            content = content[0].get("text", "") if content else ""

        raw = json.loads(content)

        groundedness = round(max(0.0, min(5.0, float(raw["groundedness"]))), 1)
        relevance    = round(max(0.0, min(5.0, float(raw["relevance"]))),    1)
        completeness = round(max(0.0, min(5.0, float(raw["completeness"]))), 1)
        overall      = round((groundedness + relevance + completeness) / 3,  1)

        return {
            "groundedness": groundedness,
            "relevance":    relevance,
            "completeness": completeness,
            "overall":      overall,
            "reasoning":    str(raw.get("reasoning", "")).strip(),
        }

    except Exception as e:
        print(f"[Evaluation] Failed: {type(e).__name__}: {e}")
        return None
