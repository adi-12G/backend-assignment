from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    bookings = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class DiagnosticCentre(Base):
    __tablename__ = "diagnostic_centres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    location = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    centre_tests = relationship(
        "CentreTest",
        back_populates="centre",
        cascade="all, delete-orphan",
    )

    bookings = relationship(
        "Booking",
        back_populates="centre",
    )


class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    centre_tests = relationship(
        "CentreTest",
        back_populates="test",
        cascade="all, delete-orphan",
    )

    bookings = relationship(
        "Booking",
        back_populates="test",
    )


class CentreTest(Base):
    __tablename__ = "centre_tests"

    id = Column(Integer, primary_key=True, index=True)

    centre_id = Column(
        Integer,
        ForeignKey("diagnostic_centres.id"),
        nullable=False,
    )

    test_id = Column(
        Integer,
        ForeignKey("diagnostic_tests.id"),
        nullable=False,
    )

    price = Column(
        Numeric(10, 2),
        nullable=False,
    )

    centre = relationship(
        "DiagnosticCentre",
        back_populates="centre_tests",
    )

    test = relationship(
        "DiagnosticTest",
        back_populates="centre_tests",
    )

    __table_args__ = (
        UniqueConstraint(
            "centre_id",
            "test_id",
            name="uq_centre_test",
        ),
    )


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    centre_id = Column(
        Integer,
        ForeignKey("diagnostic_centres.id"),
        nullable=False,
    )

    test_id = Column(
        Integer,
        ForeignKey("diagnostic_tests.id"),
        nullable=False,
    )

    appointment_datetime = Column(
        DateTime,
        nullable=False,
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False,
    )

    status = Column(
        Enum(
            "PENDING",
            "CONFIRMED",
            "FAILED",
            "CANCELLED",
            name="booking_status",
        ),
        nullable=False,
        default="PENDING",
    )

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="bookings",
    )

    centre = relationship(
        "DiagnosticCentre",
        back_populates="bookings",
    )

    test = relationship(
        "DiagnosticTest",
        back_populates="bookings",
    )

    payment = relationship(
        "Payment",
        back_populates="booking",
        uselist=False,
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=False,
        unique=True,
    )

    provider_payment_id = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    event_id = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False,
    )

    status = Column(
        Enum(
            "SUCCESS",
            "FAILED",
            name="payment_status",
        ),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    booking = relationship(
        "Booking",
        back_populates="payment",
    )