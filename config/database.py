from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import make_url
from config.settings import settings


def ensure_database_exists(database_url: str):
    """Checks if the database exists and creates it if it is missing (PostgreSQL only)"""
    if "postgresql" in database_url:
        try:
            url = make_url(database_url)
            db_name = url.database
            if db_name:
                postgres_url = url.set(database="postgres")
                temp_engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
                with temp_engine.connect() as conn:
                    result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
                    exists = result.scalar()
                    if not exists:
                        conn.execute(text(f"CREATE DATABASE {db_name}"))
                        print(f"[DB] Created database '{db_name}' automatically.")
                temp_engine.dispose()
        except Exception as e:
            print(f"[DB ERROR] Failed to verify/create database: {e}")


# Ensure database exists before creating the engine
ensure_database_exists(settings.database_url)

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
