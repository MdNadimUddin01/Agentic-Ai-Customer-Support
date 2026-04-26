"""Chat endpoint for customer support conversations."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from pymongo.errors import DuplicateKeyError
from config import logger, settings
from src.core.database import get_collection, COLLECTION_CONVERSATIONS
from src.core.constants import Channel, MessageRole, ConversationStatus
from src.core.confidence import calculate_confidence_score
from src.core.mini_rag import retrieve_knowledge_context
from src.models.customer import Customer
from src.api.routes.auth import get_current_customer
from src.agents.intent_classifier import intent_classifier
from src.agents.technical_agent import TechnicalAgent
from src.agents.account_agent import AccountAgent
from src.agents.query_agent import QueryAgent
from src.agents.escalation_agent import EscalationAgent
from src.tools import (
    KnowledgeSearchTool,
    GetSubscriptionTool,
    UpdateSubscriptionTool,
    VerifyAccountTool,
    CheckBillingTool,
    RunDiagnosticTool,
    CheckServiceStatusTool,
    CreateTicketTool,
    OrderTrackingTool,
)
from src.core.constants import AgentType, TicketCategory

router = APIRouter()


def _resolve_conversation_id(request_session_id: Optional[str], request_conversation_id: Optional[str]) -> str:
    """Resolve a stable conversation id from session_id or conversation_id."""
    if request_session_id:
        return request_session_id
    if request_conversation_id:
        return request_conversation_id
    return f"conv_{uuid.uuid4().hex[:12]}"


def _create_message_payload(role: MessageRole, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build a message payload for persistence."""
    return {
        "role": role.value,
        "content": content,
        "timestamp": datetime.utcnow(),
        "metadata": metadata or {}
    }


def _get_or_create_conversation(
    conversation_id: str,
    customer_id: str,
    channel: Channel,
    industry: str
) -> Dict[str, Any]:
    """Get existing conversation from MongoDB or create a new one."""
    conversations_coll = get_collection(COLLECTION_CONVERSATIONS)
    conversation = conversations_coll.find_one({"conversation_id": conversation_id})

    if conversation:
        if conversation.get("customer_id") != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This conversation belongs to a different customer"
            )
        return conversation

    now = datetime.utcnow()
    conversation = {
        "conversation_id": conversation_id,
        "customer_id": customer_id,
        "channel": channel,
        "industry": industry,
        "messages": [],
        "context": {},
        "status": ConversationStatus.ACTIVE,
        "created_at": now,
        "updated_at": now,
    }

    try:
        conversations_coll.insert_one(conversation)
        return conversation
    except DuplicateKeyError:
        # Concurrent request may have created it first
        conversation = conversations_coll.find_one({"conversation_id": conversation_id})
        if conversation and conversation.get("customer_id") == customer_id:
            return conversation
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conversation creation conflict"
        )


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    customer_id: str = Field(..., description="Customer ID")
    channel: Channel = Field(default=Channel.WEB, description="Communication channel")
    conversation_id: Optional[str] = Field(None, description="Deprecated alias for session ID")
    session_id: Optional[str] = Field(None, description="Session ID for conversation isolation")
    industry: str = Field(default="saas", description="Industry context")


class ChatResponse(BaseModel):
    """Chat response schema."""
    response: str
    conversation_id: str
    timestamp: datetime
    intent: Optional[str] = None
    confidence_score: Optional[float] = None
    agent_type: Optional[str] = None
    escalated: bool = False
    ticket_id: Optional[str] = None


class ConversationSummary(BaseModel):
    """Conversation summary for history list."""
    conversation_id: str
    status: str
    message_count: int
    preview: Optional[str] = None
    updated_at: datetime


@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(current_customer: Customer = Depends(get_current_customer), limit: int = 20):
    """List persisted conversations for the authenticated customer."""
    try:
        safe_limit = max(1, min(limit, 100))
        conversations_coll = get_collection(COLLECTION_CONVERSATIONS)
        rows = list(
            conversations_coll.find(
                {"customer_id": current_customer.customer_id},
                {
                    "_id": 0,
                    "conversation_id": 1,
                    "status": 1,
                    "messages": 1,
                    "updated_at": 1
                }
            )
            .sort("updated_at", -1)
            .limit(safe_limit)
        )

        summaries: List[ConversationSummary] = []
        for row in rows:
            messages = row.get("messages", [])
            last_assistant = next(
                (msg.get("content") for msg in reversed(messages) if msg.get("role") == MessageRole.ASSISTANT.value),
                None
            )
            preview = (last_assistant or (messages[-1].get("content") if messages else ""))[:140] or None

            summaries.append(ConversationSummary(
                conversation_id=row.get("conversation_id"),
                status=row.get("status", ConversationStatus.ACTIVE),
                message_count=len(messages),
                preview=preview,
                updated_at=row.get("updated_at", datetime.utcnow())
            ))

        return summaries

    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, current_customer: Customer = Depends(get_current_customer)):
    """
    Main chat endpoint for customer support.

    Args:
        request: Chat request

    Returns:
        AI agent response
    """
    try:
        if request.customer_id != current_customer.customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only chat using your own customer account"
            )

        logger.info(f"Chat request from customer {request.customer_id}: {request.message[:100]}...")

        conversation_id = _resolve_conversation_id(request.session_id, request.conversation_id)
        conversation = _get_or_create_conversation(
            conversation_id=conversation_id,
            customer_id=request.customer_id,
            channel=request.channel,
            industry=request.industry
        )
        conversations_coll = get_collection(COLLECTION_CONVERSATIONS)

        # Persist user message with timestamp
        user_message = _create_message_payload(
            role=MessageRole.USER,
            content=request.message
        )
        conversations_coll.update_one(
            {"conversation_id": conversation_id},
            {
                "$push": {"messages": user_message},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        # Conversation history for model prompt (windowed)
        history_for_model = (conversation.get("messages", []) + [user_message])[-settings.max_conversation_history:]
        history_for_model_simple = [
            {"role": msg.get("role"), "content": msg.get("content")}
            for msg in history_for_model
        ]

        # Week 4: retrieve domain knowledge (mini-RAG)
        rag_context, rag_results = retrieve_knowledge_context(
            query=request.message,
            industry=request.industry,
            top_k=3
        )

        # Week 3: dedicated LLM intent classification
        intent_label = intent_classifier.classify(
            message=request.message,
            conversation_history=history_for_model_simple,
            industry=request.industry
        )

        # Route to appropriate agent (Week 3 intent -> existing agent types)
        if intent_label == "technical_issue":
            agent_type = AgentType.TECHNICAL
        elif intent_label == "payment_issue":
            agent_type = AgentType.ACCOUNT
        elif intent_label == "account_management":
            agent_type = AgentType.ACCOUNT
        elif intent_label == "order_status":
            agent_type = AgentType.ORDER
        elif intent_label == "complaint":
            agent_type = AgentType.ESCALATION
        else:
            agent_type = AgentType.QUERY

        # Process with agent
        agent_response, escalated, ticket_id, agent_runtime = process_with_agent(
            agent_type=agent_type,
            message=request.message,
            customer_id=request.customer_id,
            session_id=conversation_id,
            conversation_history=history_for_model_simple,
            retrieved_context=rag_context,
            industry=request.industry
        )

        # Week 6: confidence scoring + threshold escalation
        confidence_score = calculate_confidence_score(
            user_message=request.message,
            response=agent_response,
            intent_label=intent_label,
            agent_type=agent_type,
            rag_results=rag_results,
            agent_confidence_hint=agent_runtime.get("agent_confidence"),
            found_answer=agent_runtime.get("found_answer"),
            escalated=escalated,
        )

        if confidence_score < settings.escalation_confidence_threshold and not ticket_id:
            escalation_agent = EscalationAgent()
            ticket_result = escalation_agent.create_ticket(
                conversation_id=conversation_id,
                customer_id=request.customer_id,
                issue_description=request.message,
                agent_attempts=(
                    f"Low-confidence response (score={confidence_score:.2f}, "
                    f"threshold={settings.escalation_confidence_threshold:.2f}). "
                    f"Intent={intent_label}, Agent={agent_type}."
                ),
                category=TicketCategory.GENERAL,
                industry=request.industry,
                confidence_score=confidence_score,
                source_intent=intent_label,
                escalation_reason="low_confidence"
            )
            created_ticket_id = ticket_result.get("ticket_id")
            if created_ticket_id:
                ticket_id = created_ticket_id
                escalated = True
                agent_response = ticket_result.get("message", agent_response)

        # Persist assistant message with metadata (intent + rag sources)
        assistant_message = _create_message_payload(
            role=MessageRole.ASSISTANT,
            content=agent_response,
            metadata={
                "agent_type": agent_type,
                "intent": intent_label,
                "confidence_score": confidence_score,
                "confidence_threshold": settings.escalation_confidence_threshold,
                "escalated": escalated,
                "escalation_reason": "low_confidence" if (escalated and confidence_score < settings.escalation_confidence_threshold) else None,
                "rag_sources": [
                    {
                        "id": item.get("id"),
                        "category": item.get("metadata", {}).get("category", "general"),
                        "score": item.get("score", 0),
                    }
                    for item in rag_results
                ]
            }
        )
        update_payload: Dict[str, Any] = {
            "$push": {"messages": assistant_message},
            "$set": {"updated_at": datetime.utcnow()}
        }
        if escalated:
            update_payload["$set"]["status"] = ConversationStatus.ESCALATED

        conversations_coll.update_one(
            {"conversation_id": conversation_id},
            update_payload
        )

        logger.info(f"Chat response generated for customer {request.customer_id}")

        return ChatResponse(
            response=agent_response,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            intent=intent_label,
            confidence_score=confidence_score,
            agent_type=agent_type,
            escalated=escalated,
            ticket_id=ticket_id
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )


def process_with_agent(
    agent_type: AgentType,
    message: str,
    customer_id: str,
    session_id: str,
    conversation_history: List[Dict[str, str]],
    retrieved_context: str,
    industry: str
) -> tuple[str, bool, Optional[str], Dict[str, Any]]:
    """
    Process message with appropriate agent.

    Returns:
        (response, escalated, ticket_id)
    """
    # Initialize tools
    knowledge_tool = KnowledgeSearchTool(industry=industry)
    subscription_tool = GetSubscriptionTool()
    update_sub_tool = UpdateSubscriptionTool()
    billing_tool = CheckBillingTool()
    verify_tool = VerifyAccountTool()
    diagnostic_tool = RunDiagnosticTool()
    service_status_tool = CheckServiceStatusTool()
    ticket_tool = CreateTicketTool()
    order_tracking_tool = OrderTrackingTool()

    escalated = False
    ticket_id = None
    runtime: Dict[str, Any] = {
        "agent_confidence": None,
        "found_answer": None,
    }

    message_for_agent = message
    if retrieved_context:
        message_for_agent = (
            f"User question:\n{message}\n\n"
            f"Retrieved knowledge context:\n{retrieved_context}\n\n"
            "Use this retrieved context when relevant and prioritize factual consistency."
        )

    # Use provided in-memory session history
    conv_history = conversation_history

    if agent_type == AgentType.TECHNICAL:
        # Technical agent with tools
        agent = TechnicalAgent(tools=[
            knowledge_tool,
            verify_tool,
            diagnostic_tool,
            service_status_tool,
            ticket_tool
        ])

        result = agent.handle_issue(
            message=message_for_agent,
            customer_id=customer_id,
            industry=industry,
            conversation_history=conv_history
        )

        response = result["response"]
        escalated = result["should_escalate"]
        runtime["agent_confidence"] = result.get("confidence")

        # If should escalate, create ticket
        if escalated and result["confidence"] < settings.escalation_confidence_threshold:
            escalation_agent = EscalationAgent()
            ticket_result = escalation_agent.create_ticket(
                conversation_id=session_id,
                customer_id=customer_id,
                issue_description=message,
                agent_attempts=f"Attempted {result['attempts']} times. Confidence: {result['confidence']:.2f}",
                category=TicketCategory.TECHNICAL,
                industry=industry,
                confidence_score=result.get("confidence"),
                escalation_reason="technical_low_confidence"
            )
            ticket_id = ticket_result.get("ticket_id")
            response = ticket_result.get("message", response)

    elif agent_type == AgentType.ACCOUNT:
        # Account agent with tools
        agent = AccountAgent(tools=[
            subscription_tool,
            update_sub_tool,
            billing_tool,
            verify_tool,
            ticket_tool
        ])

        result = agent.handle_request(
            message=message,
            customer_id=customer_id,
            conversation_history=conv_history
        )

        response = result["response"]
        runtime["agent_confidence"] = 0.78

    elif agent_type == AgentType.ORDER:
        # Week 7: dedicated order tracking via external courier API mock
        tracking_result = order_tracking_tool.execute(
            customer_id=customer_id,
            order_id=None,
            query_text=message,
        )
        response = tracking_result
        runtime["agent_confidence"] = 0.92
        runtime["found_answer"] = True

    elif agent_type == AgentType.QUERY:
        # Query agent with knowledge search
        agent = QueryAgent(tools=[knowledge_tool, ticket_tool])

        result = agent.answer_query(
            message=message_for_agent,
            customer_id=customer_id,
            industry=industry,
            conversation_history=conv_history
        )

        response = result["response"]
        runtime["found_answer"] = result.get("found_answer")
        runtime["agent_confidence"] = 0.8 if result.get("found_answer") else 0.45

        # Escalate if no answer found
        if not result["found_answer"]:
            escalation_agent = EscalationAgent()
            ticket_result = escalation_agent.create_ticket(
                conversation_id=session_id,
                customer_id=customer_id,
                issue_description=message,
                agent_attempts="Could not find relevant information in knowledge base",
                category=TicketCategory.GENERAL,
                industry=industry,
                confidence_score=0.35,
                escalation_reason="no_answer_found"
            )
            ticket_id = ticket_result.get("ticket_id")
            response = ticket_result.get("message", response)
            escalated = True

    elif agent_type == AgentType.ESCALATION:
        escalation_agent = EscalationAgent()
        ticket_result = escalation_agent.create_ticket(
            conversation_id=session_id,
            customer_id=customer_id,
            issue_description=message_for_agent,
            agent_attempts="Escalation requested by intent classifier",
            category=TicketCategory.GENERAL,
            industry=industry,
            confidence_score=0.2,
            escalation_reason="complaint_or_forced_escalation"
        )
        ticket_id = ticket_result.get("ticket_id")
        response = ticket_result.get(
            "message",
            "I understand your concern. I have escalated this to human support."
        )
        escalated = True

    else:
        # Fallback
        response = "I'm here to help! Could you please provide more details about your issue?"
        runtime["agent_confidence"] = 0.4

    return response, escalated, ticket_id, runtime


@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str, current_customer: Customer = Depends(get_current_customer)):
    """
    Get conversation by ID.

    Args:
        conversation_id: Conversation ID

    Returns:
        Conversation details
    """
    try:
        conversations_coll = get_collection(COLLECTION_CONVERSATIONS)
        conv_data = conversations_coll.find_one({"conversation_id": conversation_id})

        if not conv_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if conv_data.get("customer_id") != current_customer.customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to access this conversation"
            )

        conv_data.pop("_id", None)
        return conv_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
