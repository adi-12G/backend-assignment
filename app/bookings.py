from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Booking, CentreTest, User
from app.schemas import BookingCreate, BookingResponse


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check that the selected test is available
    # at the selected diagnostic centre.
    centre_test = (
        db.query(CentreTest)
        .filter(
            CentreTest.centre_id == data.centre_id,
            CentreTest.test_id == data.test_id,
        )
        .first()
    )

    if not centre_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This test is not available at the selected centre",
        )

    # Appointment must be in the future.
    appointment_time = data.appointment_datetime

    if appointment_time.tzinfo is not None:
        appointment_time = appointment_time.replace(tzinfo=None)

    current_time = datetime.now(timezone.utc).replace(tzinfo=None)

    if appointment_time <= current_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment must be in the future",
        )

    # IMPORTANT:
    # Get the price from our database.
    # Never trust the client to send the amount.
    booking = Booking(
        user_id=current_user.id,
        centre_id=data.centre_id,
        test_id=data.test_id,
        appointment_datetime=appointment_time,
        amount=centre_test.price,
        status="PENDING",
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


@router.get(
    "",
    response_model=list[BookingResponse],
)
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    return bookings


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return booking


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
)
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending bookings can be cancelled",
        )

    booking.status = "CANCELLED"

    db.commit()
    db.refresh(booking)

    return booking