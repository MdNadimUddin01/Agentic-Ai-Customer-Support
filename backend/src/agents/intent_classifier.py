"""Dedicated LLM-based intent classification for Week 3."""
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings, logger


ALLOWED_INTENTS = {
    "greeting",
    "order_status",
    "payment_issue",
    "account_management",
    "technical_issue",
    "complaint",
}


class IntentClassifier:
    """Classifies user intent using a dedicated Gemini prompt."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=0.0,
            max_tokens=20,
            google_api_key=settings.google_api_key,
            convert_system_message_to_human=True,
        )

    def _invoke_with_timeout(self, prompt: str):
        """Bound LLM classification latency so chat requests can't hang indefinitely."""
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.llm.invoke, prompt)
        try:
            return future.result(timeout=settings.agent_timeout)
        except FutureTimeoutError as exc:
            logger.error(f"Intent classification timed out after {settings.agent_timeout}s")
            raise TimeoutError(f"Intent classification timed out after {settings.agent_timeout} seconds") from exc
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def classify(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        industry: str = "saas"
    ) -> str:
        """Return one of: greeting, order_status, payment_issue, account_management, technical_issue, complaint."""
        try:
            message_lower = (message or "").strip().lower()

            account_keywords = [
                "current plan", "my plan", "subscription", "renewal", "renew", "upgrade",
                "downgrade", "billing history", "invoice", "invoices", "account settings",
                "payment history", "total purchased", "total order purchased", "how much have i paid",
            ]
            payment_keywords = [
                "payment failed", "card declined", "duplicate charge", "charged twice",
                "refund", "refund status", "billing problem", "payment issue",
            ]
            order_keywords = [
                "order", "shipment", "delivery", "tracking", "pending order", "where is my order",
                "shipped", "delivered", "processing order",
            ]
            complaint_keywords = [
                "complaint", "this is unacceptable", "i want to escalate", "speak to human",
                "talk to human", "manager", "angry", "frustrated", "bad service",
            ]
            technical_keywords = [
                "error", "bug", "not working", "login", "401", "500", "api", "issue", "broken",
            ]

            if any(keyword in message_lower for keyword in complaint_keywords):
                return "complaint"
            if any(keyword in message_lower for keyword in account_keywords):
                return "account_management"
            if any(keyword in message_lower for keyword in payment_keywords):
                return "payment_issue"
            if any(keyword in message_lower for keyword in order_keywords):
                return "order_status"
            if any(keyword in message_lower for keyword in technical_keywords):
                return "technical_issue"
            if any(message_lower.startswith(greeting) for greeting in ["hi", "hello", "hey", "thanks", "thank you"]):
                return "greeting"

            history_lines = []
            for item in conversation_history or []:
                role = item.get("role", "unknown")
                content = item.get("content", "")
                history_lines.append(f"- {role}: {content}")

            history_text = "\n".join(history_lines[-20:]) if history_lines else "(none)"

            prompt = (
                "You are an intent classifier for customer support.\n"
                "Classify the user's latest message into exactly one label:\n"
                "greeting, order_status, payment_issue, account_management, technical_issue, complaint\n\n"
                "Rules:\n"
                "- Output only the label text, no explanation.\n"
                "- If user is reporting product/service malfunction, errors, bugs, outages -> technical_issue\n"
                "- If user asks where order/package is, delivery ETA, shipment tracking -> order_status\n"
                "- If user asks about charges, failed payments, billing failures, card/payment problems -> payment_issue\n"
                "- If user asks about subscription, current plan, upgrade, downgrade, renewal, invoice history, billing history, account settings -> account_management\n"
                "- If user is upset, demanding escalation/refund due to dissatisfaction -> complaint\n"
                "- Simple hello/hi/thanks/starting conversation -> greeting\n\n"
                "- Prior conversation matters less than the latest user message; classify the latest message directly.\n\n"
                f"Industry: {industry}\n"
                f"Conversation history:\n{history_text}\n\n"
                f"Latest user message:\n{message}\n\n"
                "Label:"
            )

            response = self._invoke_with_timeout(prompt)
            label = (response.content or "").strip().lower()

            if label in ALLOWED_INTENTS:
                return label

            # Defensive fallback for unexpected model output
            for intent in ALLOWED_INTENTS:
                if intent in label:
                    return intent

            return "account_management"

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return "account_management"


intent_classifier = IntentClassifier()
