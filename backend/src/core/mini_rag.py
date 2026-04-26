"""Week 4 mini-RAG retrieval helpers."""
from typing import List, Dict, Any, Tuple
from config import logger
from src.core.vector_store import search_knowledge_base


# Small built-in FAQ corpus (fallback when DB/vector docs are missing)
MINI_FAQ_DOCS: List[Dict[str, Any]] = [
    {
        "id": "faq_001",
        "industry": "saas",
        "category": "billing",
        "content": "We retry failed payments automatically after 3, 5, and 7 days. Update your card in Settings > Billing to prevent suspension.",
    },
    {
        "id": "faq_002",
        "industry": "saas",
        "category": "billing",
        "content": "Annual plans include a 20% discount compared with monthly billing.",
    },
    {
        "id": "faq_003",
        "industry": "saas",
        "category": "authentication",
        "content": "If login fails, verify email and password, check Caps Lock, then use Forgot Password and clear browser cache.",
    },
    {
        "id": "faq_004",
        "industry": "saas",
        "category": "authentication",
        "content": "Password reset links are valid for 1 hour and may arrive in spam folders.",
    },
    {
        "id": "faq_005",
        "industry": "saas",
        "category": "api",
        "content": "401 errors usually mean missing 'Bearer' in Authorization header or expired API keys.",
    },
    {
        "id": "faq_006",
        "industry": "saas",
        "category": "api",
        "content": "429 rate-limit responses should be handled with exponential backoff and request batching.",
    },
    {
        "id": "faq_007",
        "industry": "saas",
        "category": "subscription",
        "content": "Plan upgrades apply immediately with prorated billing for the remaining cycle.",
    },
    {
        "id": "faq_008",
        "industry": "saas",
        "category": "subscription",
        "content": "Canceled subscriptions retain access until period end, and data is retained for 30 days.",
    },
    {
        "id": "faq_009",
        "industry": "saas",
        "category": "export",
        "content": "Large data exports are processed asynchronously and delivered via email link valid for 7 days.",
    },
    {
        "id": "faq_010",
        "industry": "saas",
        "category": "permissions",
        "content": "Role permissions are Admin, Member, and Viewer; Admin can manage billing and settings.",
    },
    {
        "id": "faq_011",
        "industry": "saas",
        "category": "troubleshooting",
        "content": "500 errors are often temporary. Retry and include request ID when contacting support.",
    },
    {
        "id": "faq_012",
        "industry": "saas",
        "category": "troubleshooting",
        "content": "504 timeout errors may require smaller queries or breaking operations into smaller chunks.",
    },
]


def _keyword_fallback_retrieval(query: str, industry: str, top_k: int) -> List[Dict[str, Any]]:
    """Simple keyword retrieval fallback against built-in FAQ docs."""
    query_tokens = {token.strip().lower() for token in query.split() if token.strip()}
    if not query_tokens:
        return []

    scored: List[Dict[str, Any]] = []
    for doc in MINI_FAQ_DOCS:
        if doc.get("industry") != industry:
            continue

        content_tokens = {token.strip(".,:;!?()[]{}\"'").lower() for token in doc.get("content", "").split()}
        overlap = len(query_tokens.intersection(content_tokens))
        if overlap > 0:
            scored.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": {
                    "category": doc.get("category", "general"),
                    "industry": doc.get("industry", "saas"),
                    "source": "mini_faq",
                },
                "score": float(overlap),
            })

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


def retrieve_knowledge_context(query: str, industry: str = "saas", top_k: int = 3) -> Tuple[str, List[Dict[str, Any]]]:
    """Retrieve context for prompt injection using embeddings first, then keyword fallback."""
    results: List[Dict[str, Any]] = []

    try:
        results = search_knowledge_base(query=query, top_k=top_k, industry=industry)
    except Exception as e:
        logger.warning(f"Vector retrieval unavailable, using keyword fallback: {e}")

    if not results:
        results = _keyword_fallback_retrieval(query=query, industry=industry, top_k=top_k)

    if not results:
        return "", []

    context_lines = [
        "Use the following business knowledge when answering.",
        "If nothing here is relevant, answer normally and say you are unsure when needed.",
        "",
    ]

    for idx, item in enumerate(results, 1):
        metadata = item.get("metadata", {})
        category = metadata.get("category", "general")
        source = metadata.get("source", "knowledge_base")
        content = item.get("content", "")
        context_lines.append(f"[{idx}] category={category} source={source}")
        context_lines.append(content.strip())
        context_lines.append("")

    return "\n".join(context_lines).strip(), results
