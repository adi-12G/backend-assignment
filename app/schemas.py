from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TestResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CentreTestResponse(BaseModel):
    test_id: int
    test_name: str
    price: float


class CentreResponse(BaseModel):
    id: int
    name: str
    location: str
    tests: list[CentreTestResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    centre_id: int
    test_id: int
    appointment_datetime: datetime


class BookingResponse(BaseModel):
    id: int
    centre_id: int
    test_id: int
    appointment_datetime: datetime
    amount: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(BaseModel):
    booking_id: int
    simulate_success: bool = True


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    provider_payment_id: str
    event_id: str | None = None
    amount: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)


class PaymentWebhook(BaseModel):
    event_id: str
    provider_payment_id: str
    status: str