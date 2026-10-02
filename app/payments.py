import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Booking, Payment, User
from app.schemas import PaymentCreate, PaymentResponse, PaymentWebhook


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Find the booking belonging to the logged-in user
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == data.booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    # Payment is allowed only for pending bookings
    if booking.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment can only be made for a pending booking",
        )

    # Prevent duplicate payments for the same booking
    existing_payment = (
        db.query(Payment)
        .filter(Payment.booking_id == booking.id)
        .first()
    )

    if existing_payment:
        return existing_payment

    # Generate a mock provider payment ID
    provider_payment_id = f"mock_{uuid.uuid4().hex}"

    # Simulate payment result
    payment_status = (
        "SUCCESS"
        if data.simulate_success
        else "FAILED"
    )

    # Create payment
    # event_id is intentionally NULL here.
    # It will be stored when the webhook is received.
    payment = Payment(
        booking_id=booking.id,
        provider_payment_id=provider_payment_id,
        amount=booking.amount,
        status=payment_status,
    )

    # Update booking based on mock payment result
    booking.status = (
        "CONFIRMED"
        if payment_status == "SUCCESS"
        else "FAILED"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@router.post("/webhook")
def payment_webhook(
    data: PaymentWebhook,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # 1. Check whether this webhook event was already processed
    # ---------------------------------------------------------
    payment = (
        db.query(Payment)
        .filter(Payment.event_id == data.event_id)
        .first()
    )

    if payment:
        return {
            "message": "Webhook already processed",
            "payment_id": payment.id,
            "status": payment.status,
        }

    # ---------------------------------------------------------
    # 2. Find the payment using the provider payment ID
    # ---------------------------------------------------------
    payment = (
        db.query(Payment)
        .filter(
            Payment.provider_payment_id
            == data.provider_payment_id
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    # ---------------------------------------------------------
    # 3. Validate webhook status
    # ---------------------------------------------------------
    if data.status not in ["SUCCESS", "FAILED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment status",
        )

    # ---------------------------------------------------------
    # 4. Process webhook
    # ---------------------------------------------------------
    payment.status = data.status

    # Store event ID AFTER successfully finding the payment.
    # This makes repeated webhook events idempotent.
    payment.event_id = data.event_id

    # ---------------------------------------------------------
    # 5. Update booking status
    # ---------------------------------------------------------
    booking = (
        db.query(Booking)
        .filter(Booking.id == payment.booking_id)
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if data.status == "SUCCESS":
        booking.status = "CONFIRMED"
    else:
        booking.status = "FAILED"

    # ---------------------------------------------------------
    # 6. Save changes
    # ---------------------------------------------------------
    db.commit()
    db.refresh(payment)

    return {
        "message": "Webhook processed successfully",
        "payment_id": payment.id,
        "booking_id": booking.id,
        "status": payment.status,
    }