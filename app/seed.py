from app.database import SessionLocal
from app.models import DiagnosticCentre, DiagnosticTest, CentreTest


def seed_database():
    db = SessionLocal()

    try:
        # Don't duplicate seed data
        if db.query(DiagnosticCentre).first():
            print("Database already contains data.")
            return

        # Tests
        cbc = DiagnosticTest(
            name="Complete Blood Count",
            description="Basic blood test to evaluate overall health.",
        )

        hba1c = DiagnosticTest(
            name="HbA1c",
            description="Measures average blood sugar levels.",
        )

        lipid = DiagnosticTest(
            name="Lipid Profile",
            description="Measures cholesterol and triglyceride levels.",
        )

        thyroid = DiagnosticTest(
            name="Thyroid Profile",
            description="Measures thyroid-related hormone levels.",
        )

        db.add_all([
            cbc,
            hba1c,
            lipid,
            thyroid,
        ])

        db.flush()

        # Centres
        delhi = DiagnosticCentre(
            name="EVE Diagnostics Delhi",
            location="New Delhi",
        )

        noida = DiagnosticCentre(
            name="EVE Diagnostics Noida",
            location="Noida",
        )

        db.add_all([
            delhi,
            noida,
        ])

        db.flush()

        # Centre → Test relationships + prices
        db.add_all([
            CentreTest(
                centre_id=delhi.id,
                test_id=cbc.id,
                price=500,
            ),
            CentreTest(
                centre_id=delhi.id,
                test_id=hba1c.id,
                price=700,
            ),
            CentreTest(
                centre_id=delhi.id,
                test_id=lipid.id,
                price=900,
            ),
            CentreTest(
                centre_id=noida.id,
                test_id=cbc.id,
                price=450,
            ),
            CentreTest(
                centre_id=noida.id,
                test_id=thyroid.id,
                price=800,
            ),
        ])

        db.commit()

        print("Seed data created successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()