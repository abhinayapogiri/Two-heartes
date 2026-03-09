import os
import sys
from sqlalchemy import text, inspect

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, Base, SessionLocal
from utils.password import get_password_hash

# Import all models to ensure they are registered with Base.metadata
from models.user import User
from models.movie import Movie
from models.theatre import Theatre
from models.screen import Screen
from models.seat import Seat
from models.show import Show
from models.booking import Booking, BookingSeat
from models.review import Review
from models.notification import Notification
from models.payment import Payment

# --- ESSENTIAL SEED DATA ---
# We keep these so the app is usable immediately after setup.
INITIAL_USERS = [
    {
        "name": "Merchant Test",
        "email": "merchant@test.com",
        "mobile": "7396787133",
        "password": "password123",
        "is_merchant": True
    },
    {
        "name": "Admin User",
        "email": "admin@test.com",
        "mobile": "1234567890",
        "password": "admin123",
        "is_admin": True
    }
]

def sync_schema():
    """
    Automatically detects missing columns in the database by comparing 
    SQLAlchemy models with the actual database schema and adds them.
    """
    print("Checking for missing columns automatically...")
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # Iterate through all tables defined in our models
        for table_name, table in Base.metadata.tables.items():
            if not inspector.has_table(table_name):
                continue
                
            # Get existing columns in the DB
            existing_columns = [c['name'] for c in inspector.get_columns(table_name)]
            
            # Check each column in the model
            for column in table.columns:
                if column.name not in existing_columns:
                    print(f"Adding missing column '{table_name}.{column.name}'...")
                    
                    # Prepare the ALTER TABLE statement
                    # Note: This is a basic implementation. For production, use Alembic.
                    col_type = str(column.type.compile(engine.dialect))
                    
                    # Handle constraints and defaults
                    nullable = "" if column.nullable else " NOT NULL"
                    default = ""
                    if column.server_default is not None:
                        # This is a bit complex for a simple script, but handle common ones
                        default = f" DEFAULT {column.server_default.arg.text}"
                    
                    try:
                        query = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type}{nullable}{default}"
                        conn.execute(text(query))
                        conn.commit()
                        print(f"Successfully added '{column.name}' to '{table_name}'.")
                    except Exception as e:
                        print(f"Error adding column {column.name} to {table_name}: {e}")
                        conn.rollback()

def setup_db(reset=False):
    print("--- Starting Database Setup (Schema Sync) ---")
    
    if reset:
        print("Dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped.")

    print("Ensuring all tables exist...")
    Base.metadata.create_all(bind=engine)
    print("Base tables verified.")

    # Run schema sync for existing databases
    sync_schema()

    db = SessionLocal()
    try:
        # Seed Essential Users only
        print("Ensuring initial users exist...")
        for u_data in INITIAL_USERS:
            exists = db.query(User).filter(
                (User.email == u_data["email"]) | (User.mobile == u_data["mobile"])
            ).first()
            if not exists:
                user = User(
                    name=u_data["name"],
                    email=u_data["email"],
                    mobile=u_data["mobile"],
                    password_hash=get_password_hash(u_data["password"]),
                    is_merchant=u_data.get("is_merchant", False),
                    is_admin=u_data.get("is_admin", False),
                    is_verified=True
                )
                db.add(user)
                print(f"Created user: {u_data['email']}")
        db.commit()

        print("--- Database Setup Complete ---")
        print("NOTE: Sample Movies, Theatres, and Shows were NOT included as requested.")

    except Exception as e:
        print(f"Error during setup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_arg = "--reset" in sys.argv
    setup_db(reset=reset_arg)
