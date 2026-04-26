"""Authentication endpoints and dependencies."""
from datetime import datetime
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from pydantic import BaseModel, EmailStr, Field, model_validator

from config import logger
from src.core.database import COLLECTION_CUSTOMERS, get_collection
from src.core.security import create_access_token, decode_access_token, hash_password, verify_password
from src.models.customer import Customer, CustomerResponse


router = APIRouter()
security = HTTPBearer(auto_error=False)


class RegisterRequest(BaseModel):
    """Registration request schema."""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    industry: str = Field(default="saas")


class LoginRequest(BaseModel):
    """Login request schema."""

    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)

    @model_validator(mode="after")
    def validate_identifier(self) -> "LoginRequest":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone is required")
        return self


class AuthResponse(BaseModel):
    """Authentication response."""

    access_token: str
    token_type: str = "bearer"
    customer: CustomerResponse


def _build_customer_response(customer: Customer) -> CustomerResponse:
    return CustomerResponse.from_customer(customer)


def _get_customer_by_email(email: str) -> Optional[dict]:
    customers = get_collection(COLLECTION_CUSTOMERS)
    return customers.find_one({"email": email.lower().strip()})


def _get_customer_by_phone(phone: str) -> Optional[dict]:
    customers = get_collection(COLLECTION_CUSTOMERS)
    return customers.find_one({"phone": phone.strip()})


def get_current_customer(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Customer:
    """Resolve the authenticated customer from the bearer token."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    try:
        payload = decode_access_token(credentials.credentials)
        customer_id = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        ) from exc

    if not customer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    customers = get_collection(COLLECTION_CUSTOMERS)
    customer_data = customers.find_one({"customer_id": customer_id})
    if not customer_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found"
        )

    return Customer.from_dict(customer_data)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Create a user account and return an access token."""
    customers = get_collection(COLLECTION_CUSTOMERS)
    normalized_email = request.email.lower().strip()
    normalized_phone = request.phone.strip() if request.phone else None

    if _get_customer_by_email(normalized_email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

    if normalized_phone and _get_customer_by_phone(normalized_phone):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this phone number already exists"
        )

    customer = Customer(
        customer_id=f"cust_{uuid.uuid4().hex[:8]}",
        name=request.name.strip(),
        email=normalized_email,
        phone=normalized_phone,
        password_hash=hash_password(request.password),
        industry=request.industry,
        preferences={"notification_email": True},
        metadata={"created_via": "web_signup"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    customers.insert_one(customer.to_dict())
    logger.info(f"Created customer account: {customer.customer_id}")

    token = create_access_token(
        subject=customer.customer_id,
        extra_claims={"email": customer.email}
    )

    return AuthResponse(
        access_token=token,
        customer=_build_customer_response(customer)
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Authenticate an existing user account."""
    customer_data = None

    if request.email:
        customer_data = _get_customer_by_email(request.email)
    elif request.phone:
        customer_data = _get_customer_by_phone(request.phone)

    if not customer_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    customer = Customer.from_dict(customer_data)
    if not customer.password_hash or not verify_password(request.password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(
        subject=customer.customer_id,
        extra_claims={"email": customer.email}
    )

    return AuthResponse(
        access_token=token,
        customer=_build_customer_response(customer)
    )


@router.get("/me", response_model=CustomerResponse)
async def me(current_customer: Customer = Depends(get_current_customer)):
    """Return the authenticated user's profile."""
    return _build_customer_response(current_customer)