from sqlalchemy import text
from core.database import SessionLocal

def clear_seeded_data():
    db = SessionLocal()
    try:
        print("--- Clearing Seeded Data (Keeping Users) ---")
        
        # List of tables to truncate
        # Order matters for foreign key constraints
        tables = [
            "payments",
            "notifications",
            "reviews",
            "booking_seats",
            "bookings",
            "shows",
            "seats",
            "screens",
            "theatres",
            "movies"
        ]
        
        for table in tables:
            print(f"Clearing table: {table}")
            db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
        
        db.commit()
        print("\nSuccessfully cleared all seeded data.")
        print("The 'users' table remains intact.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_seeded_data()
