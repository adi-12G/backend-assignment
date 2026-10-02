from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DiagnosticCentre, DiagnosticTest
from app.schemas import CentreResponse, TestResponse


router = APIRouter(
    tags=["Centres & Tests"],
)


@router.get(
    "/centres",
    response_model=list[CentreResponse],
)
def get_centres(
    db: Session = Depends(get_db),
):
    centres = db.query(DiagnosticCentre).all()

    result = []

    for centre in centres:
        tests = []

        for centre_test in centre.centre_tests:
            tests.append(
                {
                    "test_id": centre_test.test.id,
                    "test_name": centre_test.test.name,
                    "price": float(centre_test.price),
                }
            )

        result.append(
            {
                "id": centre.id,
                "name": centre.name,
                "location": centre.location,
                "tests": tests,
            }
        )

    return result


@router.get(
    "/centres/{centre_id}",
    response_model=CentreResponse,
)
def get_centre(
    centre_id: int,
    db: Session = Depends(get_db),
):
    centre = (
        db.query(DiagnosticCentre)
        .filter(DiagnosticCentre.id == centre_id)
        .first()
    )

    if not centre:
        raise HTTPException(
            status_code=404,
            detail="Diagnostic centre not found",
        )

    tests = []

    for centre_test in centre.centre_tests:
        tests.append(
            {
                "test_id": centre_test.test.id,
                "test_name": centre_test.test.name,
                "price": float(centre_test.price),
            }
        )

    return {
        "id": centre.id,
        "name": centre.name,
        "location": centre.location,
        "tests": tests,
    }


@router.get(
    "/tests",
    response_model=list[TestResponse],
)
def get_tests(
    db: Session = Depends(get_db),
):
    return db.query(DiagnosticTest).all()


@router.get(
    "/tests/{test_id}",
    response_model=TestResponse,
)
def get_test(
    test_id: int,
    db: Session = Depends(get_db),
):
    test = (
        db.query(DiagnosticTest)
        .filter(DiagnosticTest.id == test_id)
        .first()
    )

    if not test:
        raise HTTPException(
            status_code=404,
            detail="Diagnostic test not found",
        )

    return test